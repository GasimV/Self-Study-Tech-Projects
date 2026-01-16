import torch
import torch.nn as nn
from llm_architecture import GPTModel
from gpt_config import GPT_CONFIG_124M
from utility import train_model_simple, evaluate_model, generate_and_print_sample


torch.manual_seed(123)
model = GPTModel(GPT_CONFIG_124M)
model.to(device)
optimizer = torch.optim.AdamW(
     model.parameters(),           #1 The .parameters() method returns all trainable weight parameters of the model. 
    lr=0.0004, weight_decay=0.1
)
num_epochs = 10
train_losses, val_losses, tokens_seen = train_model_simple(
    model, train_loader, val_loader, optimizer, device,
    num_epochs=num_epochs, eval_freq=5, eval_iter=5,
    start_context="Every effort moves you", tokenizer=tokenizer
)