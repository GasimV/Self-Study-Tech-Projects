#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import argparse
import torch
import re
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

DEFAULT_BASE_ID  = "unsloth/gemma-3-4b-pt"
DEFAULT_FT_DIR   = "/.../cpt/checkpoint_100_merged"
DEFAULT_LORA_DIR = "/.../cpt/checkpoint-6700"

AZ_SYSTEM = (
    "Sən Azərbaycan dilində danışan çağrı mərkəzi agentisən. "
    "Cavabların qısa, nəzakətli və addım-addım olmalıdır. "
    "Müştərinin problemini dəqiqləşdirmək üçün ən çox 2 sual ver. "
    "Heç vaxt kart nömrəsi, CVV, PIN, şifrə/parol kimi həssas məlumat istəmə. "
    "Əgər şəxsiyyəti təsdiqləmək lazımdırsa, yalnız təhlükəsiz məlumatlarla yönləndir "
    "(məsələn: müqavilə nömrəsi, son ödəniş məbləği, qeydiyyat nömrəsi və s.). "
    "Zəruri olduqda müştərini düzgün kanala yönləndir və eskalasiya qaydasını izah et."
)

def pick_dtype() -> torch.dtype:
    if torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability(0)
        return torch.bfloat16 if major >= 8 else torch.float16
    return torch.float32

def load_model(path_or_id: str, dtype: torch.dtype):
    m = AutoModelForCausalLM.from_pretrained(
        path_or_id,
        torch_dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    m.eval()
    return m

def build_plain_prompt(system_text: str, user_text: str) -> str:
    # One stable format for all models (fair benchmark)
    return (
        "SYSTEM:\n" + system_text.strip() + "\n\n"
        "USER:\n" + user_text.strip() + "\n\n"
        "ASSISTANT:\n"
    )

@torch.no_grad()
def generate_plain(model, tokenizer, prompt: str, max_new_tokens: int, temperature: float, top_p: float):
    inputs = tokenizer(prompt, return_tensors="pt")

    # move to model device
    try:
        dev = model.device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
    except Exception:
        pass

    prompt_len = int(inputs["input_ids"].shape[-1])

    t0 = time.time()
    out = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=(temperature > 0),
        temperature=temperature,
        top_p=top_p,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )

    dt = time.time() - t0

    gen_ids = out[0, prompt_len:]
    text = tokenizer.decode(gen_ids, skip_special_tokens=True)
    text = re.split(r"\n\s*(USER|SYSTEM|ASSISTANT)\s*:", text, maxsplit=1)[0].strip()
    visible_tokens = tokenizer(text, add_special_tokens=False).input_ids
    gen_tokens = len(visible_tokens)
    tps = gen_tokens / dt

    return text, dt, gen_tokens, tps

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE_ID)
    ap.add_argument("--ft", default=DEFAULT_FT_DIR)
    ap.add_argument("--lora", default=DEFAULT_LORA_DIR)
    ap.add_argument("--max_new_tokens", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top_p", type=float, default=1.0)
    ap.add_argument("--no_ft", action="store_true", help="Compare only base vs FT+LoRA (skip FT output).")
    args = ap.parse_args()

    dtype = pick_dtype()
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'} | dtype: {dtype}")

    # Use ONE tokenizer (from base) for all variants for fairness and to avoid config drift
    tok_src = args.ft if os.path.isdir(args.ft) else args.base
    tokenizer = AutoTokenizer.from_pretrained(tok_src, use_fast=True, trust_remote_code=True)


    print("\nLoading BASE:", args.base)
    base_model = load_model(args.base, dtype)

    print("Loading FT checkpoint:", args.ft)
    ft_model = load_model(args.ft, dtype)

    print("Loading LoRA adapter on FT:", args.lora)
    ft_lora_model = PeftModel.from_pretrained(ft_model, args.lora)
    ft_lora_model.eval()

    system_prompt = AZ_SYSTEM
    print("\nReady. Type a customer message. Commands: /exit  /sys <new system prompt>\n")

    while True:
        user_text = input("USER> ").strip()
        if not user_text:
            continue
        if user_text.lower() in ("/exit", "/quit"):
            break
        if user_text.startswith("/sys "):
            system_prompt = user_text[len("/sys "):].strip()
            print("System prompt updated.\n")
            continue

        prompt = build_plain_prompt(system_prompt, user_text)

        base_out, base_dt, base_tok, base_tps = generate_plain(
            base_model, tokenizer, prompt, args.max_new_tokens, args.temperature, args.top_p
        )

        if not args.no_ft:
            ft_out, ft_dt, ft_tok, ft_tps = generate_plain(
                ft_model, tokenizer, prompt, args.max_new_tokens, args.temperature, args.top_p
            )

        lora_out, lora_dt, lora_tok, lora_tps = generate_plain(
            ft_lora_model, tokenizer, prompt, args.max_new_tokens, args.temperature, args.top_p
        )

        print("\n--- BASE ---")
        print(base_out)
        print(f"[{base_tok} toks | {base_dt:.2f}s | {base_tps:.1f} tok/s]")

        if not args.no_ft:
            print("\n--- FT ---")
            print(ft_out)
            print(f"[{ft_tok} toks | {ft_dt:.2f}s | {ft_tps:.1f} tok/s]")

        print("\n--- FT+LoRA ---")
        print(lora_out)
        print(f"[{lora_tok} toks | {lora_dt:.2f}s | {lora_tps:.1f} tok/s]\n")

if __name__ == "__main__":
    main()
