import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_MAX_LENGTH = 8192


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gemma inference (merged checkpoint).")
    parser.add_argument(
        "--model-path",
        type=Path,
        required=True,
        help="Merged model path or HF repo id.",
    )
    parser.add_argument(
        "--tokenizer-path",
        type=Path,
        default=None,
        help="Tokenizer path or HF repo id (defaults to model-path).",
    )
    parser.add_argument(
        "--chat-template",
        type=Path,
        default=None,
        help="Optional Jinja chat template file.",
    )
    parser.add_argument(
        "--fix-mistral-regex",
        action="store_true",
        help="Apply tokenizer regex fix if supported.",
    )
    parser.add_argument("--prompt", type=str, default=None, help="Single user prompt.")
    parser.add_argument(
        "--messages",
        type=Path,
        default=None,
        help="JSON or JSONL file containing messages.",
    )
    parser.add_argument("--system", type=str, default=None, help="Optional system prompt.")
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--max-length", type=int, default=DEFAULT_MAX_LENGTH)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--top-k", type=int, default=50)
    parser.add_argument("--repetition-penalty", type=float, default=1.05)
    parser.add_argument("--do-sample", action="store_true")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start a REPL and keep model loaded between prompts.",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device selection (auto uses device_map).",
    )
    parser.add_argument("--no-repeat-ngram-size", type=int, default=0)

    return parser.parse_args()


def normalize_roles(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    normalized = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "assistant":
            role = "model"
        normalized.append({"role": role, "content": content})
    return normalized


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl(path: Path) -> List[Any]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def load_conversations(path: Path) -> List[List[Dict[str, str]]]:
    if path.suffix.lower() == ".jsonl":
        raw = _load_jsonl(path)
    else:
        raw = _load_json(path)

    conversations: List[List[Dict[str, str]]] = []

    if isinstance(raw, dict):
        if "messages" in raw:
            conversations.append(raw["messages"])
        else:
            raise ValueError("JSON object must contain a 'messages' key.")
    elif isinstance(raw, list):
        if all(isinstance(x, dict) and "role" in x for x in raw):
            conversations.append(raw)
        elif all(isinstance(x, dict) and "messages" in x for x in raw):
            conversations.extend([x["messages"] for x in raw])
        elif all(isinstance(x, list) for x in raw):
            conversations.extend(raw)
        else:
            raise ValueError("Unrecognized JSON list format for messages.")
    else:
        raise ValueError("Unsupported JSON type for messages.")

    return conversations


def build_conversations(args: argparse.Namespace) -> List[List[Dict[str, str]]]:
    conversations: List[List[Dict[str, str]]] = []

    if args.messages:
        conversations = load_conversations(args.messages)
    else:
        prompt = args.prompt
        if not prompt:
            prompt = sys.stdin.read().strip()
        if not prompt:
            raise ValueError("No prompt provided (use --prompt or --messages).")
        conversations = [[{"role": "user", "content": prompt}]]

    if args.system or args.prompt and args.messages:
        updated = []
        for convo in conversations:
            convo = list(convo)
            if args.system:
                convo.insert(0, {"role": "system", "content": args.system})
            if args.messages and args.prompt:
                convo.append({"role": "user", "content": args.prompt})
            updated.append(convo)
        conversations = updated

    return conversations


def choose_dtype() -> torch.dtype:
    if torch.cuda.is_available():
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return torch.float32


def render_fallback_prompt(convo: List[Dict[str, str]]) -> str:
    if len(convo) == 1 and convo[0].get("role") == "user":
        return convo[0].get("content", "")
    system_lines: List[str] = []
    parts: List[str] = []
    for msg in convo:
        role = msg.get("role", "user")
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            parts.append(f"User: {content}")
        elif role == "model":
            parts.append(f"Assistant: {content}")
        elif role == "system":
            system_lines.append(content)
        else:
            parts.append(f"{role}: {content}")
    header = "\n".join(system_lines).strip()
    if header:
        parts.insert(0, header)
    parts.append("Assistant:")
    return "\n\n".join([parts[0], "\n".join(parts[1:])]) if header else "\n".join(parts)


def build_generation_kwargs(args: argparse.Namespace, tokenizer: AutoTokenizer) -> Dict[str, Any]:
    gen_kwargs: Dict[str, Any] = {
        "max_new_tokens": args.max_new_tokens,
        "do_sample": args.do_sample,
        "repetition_penalty": args.repetition_penalty,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    if args.do_sample:
        gen_kwargs.update(
            {
                "temperature": args.temperature,
                "top_p": args.top_p,
                "top_k": args.top_k,
            }
        )
    else:
        # Deterministic decoding defaults (you can also add num_beams here if you want)
        pass
    if args.no_repeat_ngram_size and args.no_repeat_ngram_size > 0:
        gen_kwargs["no_repeat_ngram_size"] = args.no_repeat_ngram_size

    return gen_kwargs


def main() -> None:
    args = parse_args()
    if args.seed is not None:
        torch.manual_seed(args.seed)

    tokenizer_path = args.tokenizer_path if args.tokenizer_path else args.model_path
    tokenizer_kwargs = {}
    if args.fix_mistral_regex:
        tokenizer_kwargs["fix_mistral_regex"] = True
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, **tokenizer_kwargs)
    if args.chat_template and args.chat_template.is_file():
        tokenizer.chat_template = args.chat_template.read_text(encoding="utf-8")

    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    tokenizer.truncation_side = "left"
    tokenizer.model_max_length = args.max_length

    dtype = choose_dtype()
    model_kwargs = {
        "dtype": dtype,
        "low_cpu_mem_usage": True,
    }
    if args.device == "auto":
        model_kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(args.model_path, **model_kwargs)
    model.config.use_cache = True

    if args.device in {"cuda", "cpu"}:
        device = torch.device(args.device)
        model.to(device)
    else:
        device = model.device

    gen_kwargs = build_generation_kwargs(args, tokenizer)

    if args.interactive:
        system_prompt = args.system if args.system is not None else "you are the assistant"
        convo: List[Dict[str, str]] = []
        if system_prompt:
            convo.append({"role": "system", "content": system_prompt})
        print("Interactive mode. Type 'exit' or 'quit' to stop.")
        while True:
            try:
                user_text = input("> ").strip()
            except EOFError:
                break
            if not user_text:
                continue
            if user_text.lower() in {"exit", "quit"}:
                break
            convo.append({"role": "user", "content": user_text})
            convo = normalize_roles(convo)
            if tokenizer.chat_template:
                chat_text = tokenizer.apply_chat_template(
                    convo,
                    add_generation_prompt=True,
                    tokenize=False,
                )
            else:
                chat_text = render_fallback_prompt(convo)
            inputs = tokenizer(
                chat_text,
                return_tensors="pt",
                truncation=True,
                max_length=args.max_length,
            )
            input_ids = inputs["input_ids"].to(device)
            attention_mask = inputs["attention_mask"].to(device)

            outputs = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                **gen_kwargs,
            )

            gen_ids = outputs[0][input_ids.shape[1] :]
            text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
            print(text)
            convo.append({"role": "model", "content": text})
        return

    conversations = build_conversations(args)

    for idx, convo in enumerate(conversations, start=1):
        convo = normalize_roles(convo)
        if tokenizer.chat_template:
            chat_text = tokenizer.apply_chat_template(
                convo,
                add_generation_prompt=True,
                tokenize=False,
            )
        else:
            chat_text = render_fallback_prompt(convo)
        inputs = tokenizer(
            chat_text,
            return_tensors="pt",
            truncation=True,
            max_length=args.max_length,
        )
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)

        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **gen_kwargs,
        )

        gen_ids = outputs[0][input_ids.shape[1] :]
        text = tokenizer.decode(gen_ids, skip_special_tokens=True).strip()
        if len(conversations) > 1:
            print(f"\n=== Sample {idx} ===")
        print(text)


if __name__ == "__main__":
    main()
