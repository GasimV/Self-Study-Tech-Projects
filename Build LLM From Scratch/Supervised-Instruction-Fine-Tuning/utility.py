import torch
import torch.nn as nn
import tiktoken
import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def generate_text_simple(model, idx, max_new_tokens, context_size): #1 idx is a (batch, n_tokens) array of indices in the current context.
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -context_size:] #2 Crops current context if it exceeds the supported context size, e.g., if LLM supports only 5 tokens, and the context size is 10, then only the last 5 tokens are used as context
        with torch.no_grad():
            logits = model(idx_cond)

        logits = logits[:, -1, :]  #3 Focuses only on the last time step, so that (batch, n_token, vocab_size) becomes (batch, vocab_size)
        probas = torch.softmax(logits, dim=-1)  #4 probas has shape (batch, vocab_size).
        idx_next = torch.argmax(probas, dim=-1, keepdim=True)    #5 idx_next has shape (batch, 1).
        idx = torch.cat((idx, idx_next), dim=1)  #6 Appends sampled index to the running sequence, where idx has shape (batch, n_tokens+1)

    return idx


def text_to_token_ids(text, tokenizer):
    encoded = tokenizer.encode(text, allowed_special={'<|endoftext|>'})
    encoded_tensor = torch.tensor(encoded).unsqueeze(0)    #1 .unsqueeze(0) adds the batch dimension
    return encoded_tensor


def token_ids_to_text(token_ids, tokenizer):
    flat = token_ids.squeeze(0)                #2 Removes batch dimension
    return tokenizer.decode(flat.tolist())


def calc_loss_batch(input_batch, target_batch, model, device):
    input_batch = input_batch.to(device)   #1 The transfer to a given device allows us to transfer the data to a GPU.
    target_batch = target_batch.to(device)
    logits = model(input_batch)
    loss = torch.nn.functional.cross_entropy(
        logits.flatten(0, 1), target_batch.flatten()
    )
    return loss


def calc_loss_loader(data_loader, model, device, num_batches=None):
    total_loss = 0.
    if len(data_loader) == 0:
        return float("nan")
    elif num_batches is None:
        num_batches = len(data_loader)     #1 Iteratives over all batches if no fixed num_batches is specified 
    else:
        num_batches = min(num_batches, len(data_loader))   #2 Reduces the number of batches to match the total number of batches in the data loader if num_batches exceeds the number of batches in the data loader
    for i, (input_batch, target_batch) in enumerate(data_loader):
        if i < num_batches:
            loss = calc_loss_batch(
                input_batch, target_batch, model, device
            )
            total_loss += loss.item()    #3 Sums loss for each batch
        else:
            break
    return total_loss / num_batches    #4 Averages the loss over all batches


def train_model_simple(model, train_loader, val_loader,
                       optimizer, device, num_epochs,
                       eval_freq, eval_iter, start_context, tokenizer):
    train_losses, val_losses, track_tokens_seen = [], [], []    #1 Initializes lists to track losses and tokens seen 
    tokens_seen, global_step = 0, -1

    for epoch in range(num_epochs):    #2 Starts the main training loop
        model.train()
        for input_batch, target_batch in train_loader:
            optimizer.zero_grad()   #3 Resets loss gradients from the previous batch iteration 
            loss = calc_loss_batch(
                input_batch, target_batch, model, device
            )
            loss.backward()                     #4 Calculates loss gradients 
            optimizer.step()                    #5 Updates model weights using loss gradients 
            tokens_seen += input_batch.numel()
            global_step += 1

            if global_step % eval_freq == 0:    #6 Optional evaluation step 
                train_loss, val_loss = evaluate_model(
                    model, train_loader, val_loader, device, eval_iter)
                train_losses.append(train_loss)
                val_losses.append(val_loss)
                track_tokens_seen.append(tokens_seen)
                print(f"Ep {epoch+1} (Step {global_step:06d}): "
                      f"Train loss {train_loss:.3f}, "
                      f"Val loss {val_loss:.3f}"
                )

        generate_and_print_sample(                      #7 Prints a sample text after each epoch 
            model, tokenizer, device, start_context
        )
    return train_losses, val_losses, track_tokens_seen


def train_model(model, train_loader, val_loader, optimizer, device,
                n_epochs, eval_freq, eval_iter, start_context, tokenizer,
                warmup_steps, initial_lr=3e-05, min_lr=1e-6):

    train_losses, val_losses, track_tokens_seen, track_lrs = [], [], [], []
    tokens_seen, global_step = 0, -1

    peak_lr = optimizer.param_groups[0]["lr"]   #1 Retrieves the initial learning rate from the optimizer, assuming we use it as the peak learning rate 
    total_training_steps = len(train_loader) * n_epochs     #2 Calculates the total number of iterations in the training process 
    lr_increment = (peak_lr - initial_lr) / warmup_steps    #3 Calculates the learning rate increment during the warmup phase 

    for epoch in range(n_epochs):
        model.train()
        for input_batch, target_batch in train_loader:
            optimizer.zero_grad()
            global_step += 1

            if global_step < warmup_steps:   #4 Adjusts the learning rate based on the current phase (warmup or cosine annealing) 
                lr = initial_lr + global_step * lr_increment  
            else:
                progress = ((global_step - warmup_steps) / 
                            (total_training_steps - warmup_steps))
                lr = min_lr + (peak_lr - min_lr) * 0.5 * (
                    1 + math.cos(math.pi * progress))

            for param_group in optimizer.param_groups:   #5 Applies the calculated learning rate to the optimizer
                param_group["lr"] = lr
            track_lrs.append(lr)
            loss = calc_loss_batch(input_batch, target_batch, model, device)
            loss.backward()

            if global_step >= warmup_steps:         #6 Applies gradient clipping after the warmup phase to avoid exploding gradients 
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), max_norm=1.0
                )
 #7 Everything below here remains unchanged compared to the train_model_simple function above. 
            optimizer.step() 
            tokens_seen += input_batch.numel()

            if global_step % eval_freq == 0:
                train_loss, val_loss = evaluate_model(
                    model, train_loader, val_loader,
                    device, eval_iter
                )
                train_losses.append(train_loss)
                val_losses.append(val_loss)
                track_tokens_seen.append(tokens_seen)
                print(f"Ep {epoch+1} (Iter {global_step:06d}): "
                      f"Train loss {train_loss:.3f}, "
                      f"Val loss {val_loss:.3f}"
                )


        generate_and_print_sample(
            model, tokenizer, device, start_context
        )

    return train_losses, val_losses, track_tokens_seen, track_lrs


def evaluate_model(model, train_loader, val_loader, device, eval_iter):
    model.eval()  #1 Dropout is disabled during evaluation for stable, reproducible results. 
    with torch.no_grad(): #2 Disables gradient tracking, which is not required during evaluation, to reduce the computational overhead
        train_loss = calc_loss_loader(
            train_loader, model, device, num_batches=eval_iter
        )
        val_loss = calc_loss_loader(
            val_loader, model, device, num_batches=eval_iter
        )
    model.train()
    return train_loss, val_loss


def generate_and_print_sample(model, tokenizer, device, start_context):
    model.eval()
    context_size = model.pos_emb.weight.shape[0]
    encoded = text_to_token_ids(start_context, tokenizer).to(device)
    with torch.no_grad():
        token_ids = generate_text_simple(
            model=model, idx=encoded,
            max_new_tokens=50, context_size=context_size
        )
    decoded_text = token_ids_to_text(token_ids, tokenizer)
    print(decoded_text.replace("\n", " "))      #1 Compact print format
    model.train()


def plot_losses(epochs_seen, tokens_seen, train_losses, val_losses):
    fig, ax1 = plt.subplots(figsize=(5, 3))
    ax1.plot(epochs_seen, train_losses, label="Training loss")
    ax1.plot(
        epochs_seen, val_losses, linestyle="-.", label="Validation loss"
    )
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss")
    ax1.legend(loc="upper right")
    ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax2 = ax1.twiny()                   #1 Creates a second x-axis that shares the same y-axis
    ax2.plot(tokens_seen, train_losses, alpha=0)     #2 Invisible plot for aligning ticks 
    ax2.set_xlabel("Tokens seen")
    fig.tight_layout()
    plt.show()


