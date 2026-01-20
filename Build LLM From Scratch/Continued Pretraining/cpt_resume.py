# %%capture
# import os, re
# if "COLAB_" not in "".join(os.environ.keys()):
#     !pip install unsloth
# else:
#     # Do this only in Colab notebooks! Otherwise use pip install unsloth
#     import torch; v = re.match(r"[0-9]{1,}\.[0-9]{1,}", str(torch.__version__)).group(0)
#     xformers = "xformers==" + ("0.0.33.post1" if v=="2.9" else "0.0.32.post2" if v=="2.8" else "0.0.29.post3")
#     !pip install --no-deps bitsandbytes accelerate {xformers} peft trl triton cut_cross_entropy unsloth_zoo
#     !pip install sentencepiece protobuf "datasets==4.3.0" "huggingface_hub>=0.34.0" hf_transfer
#     !pip install --no-deps unsloth
# !pip install transformers==4.56.2
# !pip install --no-deps trl==0.22.2

# nohup python cpt.py > cpt.log 2>&1 & - run the script in the background
# nohup python cpt_resume.py > cpt_resume.log 2>&1 & - run the script in the background
# tail -f cpt.log - watch the progress of CPT
# tail -f cpt_resume.log

import os, re
import torch
import unsloth  # must be before transformers
from datasets import load_dataset
from transformers import TrainingArguments
from transformers.trainer_utils import get_last_checkpoint
from unsloth import FastLanguageModel, UnslothTrainer, UnslothTrainingArguments

# Run this to disable CCE since it is not supported for CPT
os.environ['UNSLOTH_RETURN_LOGITS'] = "1"

# Model configuration
max_seq_length = 4096
dtype = None
load_in_4bit = False

output_dir = "..."

# Resolve resume checkpoint (env override or latest in output_dir)
resume_checkpoint = "..." # os.environ.get("RESUME_CHECKPOINT")
if resume_checkpoint is None:
    resume_checkpoint = get_last_checkpoint(output_dir)
if resume_checkpoint is None:
    print(f"No checkpoint found in {output_dir}. Training from scratch.")
else:
    print(f"Resuming from checkpoint: {resume_checkpoint}")

# Load model and tokenizer
print("Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    # model_name="unsloth/gemma-3-4b-pt",
    model_name="...",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)

# Configure LoRA
print("Configuring LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r=128,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj",
                    "lm_head", "embed_tokens"],  
    lora_alpha=128,
    lora_dropout=0.001,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=True,
    loftq_config=None,
)

# Load custom JSONL datasets
print("Loading training dataset...")
train_dataset = load_dataset("json", data_files=".../.jsonl", split="train")

print("Loading validation dataset...")
eval_dataset = load_dataset("json", data_files=".../name.jsonl", split="train")

# Shuffle the training dataset for better training
print("Shuffling training dataset...")
train_dataset = train_dataset.shuffle(seed=3407)

# Show dataset info
print(f"Training dataset size: {len(train_dataset)}")
print(f"Validation dataset size: {len(eval_dataset)}")
print(f"Training sample: {train_dataset[0]}")

# Add EOS token to both datasets
EOS_TOKEN = tokenizer.eos_token

def add_eos_token(examples):
    texts = examples["text"]
    outputs = [text + EOS_TOKEN for text in texts]
    return {"text": outputs}

print("Adding EOS tokens...")
train_dataset = train_dataset.map(add_eos_token, batched=True)
eval_dataset = eval_dataset.map(add_eos_token, batched=True)

# Show memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU = {gpu_stats.name}. Max memory = {max_memory} GB.")
print(f"{start_gpu_memory} GB of memory reserved.")

# Configure trainer with validation
print("Setting up trainer...")
trainer = UnslothTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,  # Add validation dataset
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=4,
    args=UnslothTrainingArguments(
        per_device_train_batch_size=24,
        per_device_eval_batch_size=10,  # Batch size for validation
        gradient_accumulation_steps=4,
        
        # Set num_train_epochs=1 for a full run, and turn off max_steps=None.
        # Use warmup_ratio and num_train_epochs for longer runs!
        # max_steps=None,
        # warmup_steps=10,
        warmup_ratio = 0.03,
        num_train_epochs = 5,

        # Select a 2 to 10x smaller learning rate for the embedding matrices!
        learning_rate=5e-8,
        embedding_learning_rate=1e-8,
        
        # Gradient clipping to prevent exploding gradients
        max_grad_norm=0.9,
        
        logging_steps=4,
        optim="adamw_torch_fused", # adamw_8bit
        weight_decay=0.001,
        lr_scheduler_type="cosine", # linear
        seed=3407,
        output_dir=output_dir,
        report_to="none",

        # Validation configuration
        eval_strategy="steps",  # Evaluate during training
        eval_steps=100,  # Evaluate every 100 steps

        # Save checkpoints periodically
        save_strategy="steps",
        save_steps=100,
        # save_total_limit=3,
    ),
)

# Train
print("Starting training...")
trainer_stats = trainer.train(resume_from_checkpoint=resume_checkpoint)

print("Training complete!")
print(f"Training stats: {trainer_stats}")

# Print final validation loss
print(f"\nFinal validation loss: {trainer_stats.metrics.get('eval_loss', 'N/A')}")
