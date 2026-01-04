# merge_lora.py
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from safetensors import safe_open
import torch, os

#BASE = "/home/ertan/orpheustts/orpheus/ft2/outputs_lora_v1/checkpoint_2637_merged"
#BASE = "unsloth/orpheus-3b-0.1-ft"
#BASE = "unsloth/orpheus-3b-0.1-pretrained"
#LORA = "/home/ertan/orpheustts/orpheus/ft2/outputs_lora_v4_ft_over_ft/checkpoint-1318"
#TOK_DIR = "/home/ertan/orpheustts/orpheus/ft2/outputs_lora_v4_ft_over_ft"  # tokenizer burada kaydedildi
#OUT  = "/home/ertan/orpheustts/orpheus/ft2/outputs_lora_v4_ft_over_ft/checkpoint_1318_ft_over_ft_merged"
BASE    = "unsloth/gemma-3-4b-pt"
LORA    = "/workspace/ertan/Gemma-4B-Gasym/outputs/checkpoint-500"
TOK_DIR = "/workspace/ertan/Gemma-4B-Gasym/outputs/checkpoint-500"  # tokenizer burada kaydedildi
OUT     = "/workspace/ertan/Gemma-4B-Gasym/outputs/checkpoint-500/checkpoint_500_merged"
 
# 1) Doğru tokenizer (LoRA ile aynı vocab!)
tok = AutoTokenizer.from_pretrained(TOK_DIR, use_fast=True)
print("len(tok) =", len(tok))

def get_adapter_vocab_size(adapter_path: str) -> int | None:
    adapter_file = os.path.join(adapter_path, "adapter_model.safetensors")
    if not os.path.isfile(adapter_file):
        return None
    with safe_open(adapter_file, framework="pt", device="cpu") as state:
        key_candidates = [
            "base_model.model.model.language_model.embed_tokens.base_layer.weight",
            "base_model.model.model.embed_tokens.base_layer.weight",
            "base_model.model.model.language_model.embed_tokens.weight",
            "base_model.model.embed_tokens.weight",
        ]
        for key in key_candidates:
            if key in state.keys():
                return state.get_slice(key).get_shape()[0]
        for key in state.keys():
            if "embed_tokens" in key and key.endswith("weight"):
                return state.get_slice(key).get_shape()[0]
    return None
 
# 2) Base modeli yükle ve embedding'i büyüt
adapter_vocab = get_adapter_vocab_size(LORA)
target_vocab = adapter_vocab or len(tok)
if adapter_vocab and adapter_vocab != len(tok):
    print(
        f"Adapter vocab size {adapter_vocab} != tokenizer size {len(tok)}; "
        "resizing base to adapter vocab."
    )
base = AutoModelForCausalLM.from_pretrained(
    BASE,
    dtype=torch.float16,            # uyarıyı gidermek için dtype kullan
    device_map="cpu",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
)
base.resize_token_embeddings(target_vocab)
 
# 3) LoRA'yı tak ve merge et
model = PeftModel.from_pretrained(base, LORA)
merged = model.merge_and_unload()   # PEFT >= 0.10
 
# 4) Kaydet
os.makedirs(OUT, exist_ok=True)
merged.save_pretrained(OUT, safe_serialization=True)
tok.save_pretrained(OUT)
print("Merged model saved to:", OUT)
