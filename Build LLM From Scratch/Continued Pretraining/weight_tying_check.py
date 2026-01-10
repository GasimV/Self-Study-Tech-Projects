# The script checks whether input and output embeddings are tied - if both layers share the exact same weight tensor object (weight tying).

from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/gemma-3-4b-pt",
    max_seq_length = 4096,
    load_in_4bit = False,
)

# Input token embedding layer
emb = model.get_input_embeddings()      # -> nn.Embedding

# Output embedding / language modeling head
if hasattr(model, "get_output_embeddings") and model.get_output_embeddings() is not None:
    head = model.get_output_embeddings()
else:
    head = model.lm_head                # typical for most LLaMA-based models

print("emb.weight is head.weight:", emb.weight is head.weight)
# data_ptr() prints the raw memory pointer (memory addresses of the weights) of each tensor.
# If the pointers are identical, it confirms the embeddings are physically the same tensor in memory, not just equal in value.
print("emb ptr:", emb.weight.data_ptr())
print("head ptr:", head.weight.data_ptr())
