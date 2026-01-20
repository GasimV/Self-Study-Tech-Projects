import argparse, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from safetensors import safe_open

'''
python merge_cli.py \
  --base /.../checkpoint_100_merged \
  --lora /.../checkpoint-1400 \
  --tok-dir /.../checkpoint-1400 \
  --out  /.../checkpoint-1400_merged \
  --device-map cpu \
  --dtype float16

'''

def get_adapter_vocab_size(adapter_path: str):
    adapter_file = os.path.join(adapter_path, "adapter_model.safetensors")
    if not os.path.isfile(adapter_file):
        return None
    with safe_open(adapter_file, framework="pt", device="cpu") as state:
        for k in state.keys():
            if "embed_tokens" in k and k.endswith("weight"):
                return state.get_slice(k).get_shape()[0]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--lora", required=True)
    ap.add_argument("--tok-dir", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--device-map", default="auto")   # "cpu" if needed
    ap.add_argument("--dtype", default="bfloat16", choices=["float16","bfloat16","float32"])
    args = ap.parse_args()

    tok_dir = args.tok_dir or args.lora
    tok = AutoTokenizer.from_pretrained(tok_dir, use_fast=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    torch_dtype = dtype_map[args.dtype]

    adapter_vocab = get_adapter_vocab_size(args.lora)
    target_vocab = adapter_vocab or len(tok)
    print("Tokenizer size:", len(tok), "| adapter vocab:", adapter_vocab, "| target:", target_vocab)

    base = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=torch_dtype,
        device_map=args.device_map,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    base.resize_token_embeddings(target_vocab)

    model = PeftModel.from_pretrained(base, args.lora)
    merged = model.merge_and_unload()

    os.makedirs(args.out, exist_ok=True)
    merged.save_pretrained(args.out, safe_serialization=True)
    tok.save_pretrained(args.out)
    print("Saved merged model to:", args.out)

if __name__ == "__main__":
    main()