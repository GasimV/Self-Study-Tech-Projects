#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge LoRA adapter into a merged Gemma checkpoint.

Merges:
  base_merged = /.../
  lora_adapter = /.../

Outputs:
  out_dir = /.../

This produces a standalone HF model directory you can load with:
  AutoModelForCausalLM.from_pretrained(out_dir, ...)
"""

import os
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from peft import PeftModel


def pick_dtype():
    if torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability(0)
        return torch.bfloat16 if major >= 8 else torch.float16
    return torch.float32


def assert_exists(path: str, kind: str):
    if not os.path.isdir(path):
        raise FileNotFoundError(f"{kind} directory not found: {path}")


def assert_adapter_dir(path: str):
    assert_exists(path, "LoRA adapter")
    cfg = os.path.join(path, "adapter_config.json")
    if not os.path.exists(cfg):
        raise FileNotFoundError(
            f"adapter_config.json not found in: {path}\n"
            f"This does not look like a PEFT adapter directory."
        )


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_merged", default="/.../")
    ap.add_argument("--lora", default="/.../")
    ap.add_argument("--out_dir", default="/.../")
    ap.add_argument("--cpu_merge", action="store_true", help="Merge on CPU to reduce VRAM usage (slower).")
    args = ap.parse_args()

    assert_exists(args.base_merged, "Base merged model")
    assert_adapter_dir(args.lora)
    os.makedirs(args.out_dir, exist_ok=True)

    dtype = pick_dtype()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Device:", device, "| dtype:", dtype)
    print("Base merged:", args.base_merged)
    print("LoRA adapter:", args.lora)
    print("Output dir:", args.out_dir)

    # Load tokenizer (from base_merged; fallback to adapter if needed)
    tok = AutoTokenizer.from_pretrained(args.base_merged, use_fast=True, trust_remote_code=True)

    # Load base model
    # device_map="auto" is best for GPU; if cpu_merge, load to CPU explicitly.
    if args.cpu_merge or device == "cpu":
        model = AutoModelForCausalLM.from_pretrained(
            args.base_merged,
            torch_dtype=torch.float32,          # safer for CPU merge
            device_map=None,
            trust_remote_code=True,
        ).to("cpu")
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_merged,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )

    model.eval()

    # Attach LoRA
    peft_model = PeftModel.from_pretrained(model, args.lora)
    peft_model.eval()

    # Merge LoRA into base weights and unload adapter modules
    # After this, peft_model becomes a plain transformers model (no PEFT wrapper).
    print("Merging LoRA weights into base model...")
    merged_model = peft_model.merge_and_unload()

    # If we merged on GPU, it's still fine to save from GPU; but moving to CPU reduces VRAM pressure.
    try:
        merged_model.to("cpu")
    except Exception:
        pass

    # Save model + tokenizer
    print("Saving merged model...")
    merged_model.save_pretrained(args.out_dir, safe_serialization=True)
    tok.save_pretrained(args.out_dir)

    # Also save config explicitly (usually included, but safe)
    try:
        cfg = AutoConfig.from_pretrained(args.base_merged, trust_remote_code=True)
        cfg.save_pretrained(args.out_dir)
    except Exception:
        pass

    print("Done.")
    print("\nTest load command:")
    print(f'python3 -c "from transformers import AutoTokenizer, AutoModelForCausalLM; '
          f't=AutoTokenizer.from_pretrained(\'{args.out_dir}\'); '
          f'm=AutoModelForCausalLM.from_pretrained(\'{args.out_dir}\'); '
          f'print(\'loaded\', type(m))"')


if __name__ == "__main__":
    main()
