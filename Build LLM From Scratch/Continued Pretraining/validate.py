import argparse
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List

import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer

"""
python validate.py \
  --model unsloth/gemma-3-4b-pt \
  --model /.../... \
  --data /.../name.jsonl \
  --dataset-field text \
  --add-eos
"""

DEFAULT_MAX_LENGTH = 4096


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute validation loss for one or more models.")
    parser.add_argument(
        "--model",
        action="append",
        required=True,
        help="Model path or HF repo id. Repeat for multiple models.",
    )
    parser.add_argument(
        "--tokenizer",
        type=str,
        default=None,
        help="Tokenizer path or HF repo id (defaults to each model).",
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Validation dataset path (JSON/JSONL). Comma-separate multiple files.",
    )
    parser.add_argument("--dataset-field", type=str, default="text")
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--max-length", type=int, default=DEFAULT_MAX_LENGTH)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--num-proc", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--add-eos", action="store_true")
    parser.add_argument("--fix-mistral-regex", action="store_true")
    parser.add_argument("--resize-token-embeddings", action="store_true")
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Enable trust_remote_code for model/tokenizer loading.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device selection (auto uses device_map).",
    )
    return parser.parse_args()


def choose_dtype() -> torch.dtype:
    if torch.cuda.is_available():
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return torch.float32


def load_text_dataset(path_arg: str, split: str) -> Any:
    paths = [p.strip() for p in path_arg.split(",") if p.strip()]
    data_files: Dict[str, List[str] | str]
    if len(paths) == 1:
        data_files = {"train": paths[0]}
    else:
        data_files = {"train": paths}
    return load_dataset("json", data_files=data_files, split=split)


def build_tokenizer(
    tokenizer_path: str,
    fix_mistral_regex: bool,
    trust_remote_code: bool,
) -> AutoTokenizer:
    tokenizer_kwargs: Dict[str, Any] = {"trust_remote_code": trust_remote_code}
    if fix_mistral_regex:
        tokenizer_kwargs["fix_mistral_regex"] = True
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, **tokenizer_kwargs)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    tokenizer.truncation_side = "left"
    return tokenizer


def tokenize_dataset(
    dataset: Any,
    tokenizer: AutoTokenizer,
    text_field: str,
    max_length: int,
    add_eos: bool,
    num_proc: int,
) -> Any:
    if text_field not in dataset.column_names:
        raise ValueError(f"Dataset field '{text_field}' not found.")

    eos = tokenizer.eos_token or ""

    def _add_eos(text: str) -> str:
        if not add_eos or not eos:
            return text
        if text.endswith(eos):
            return text
        return text + eos

    def tokenize_batch(examples: Dict[str, List[str]]) -> Dict[str, List[List[int]]]:
        texts = [_add_eos(text) for text in examples[text_field]]
        return tokenizer(
            texts,
            truncation=True,
            max_length=max_length,
            padding=False,
        )

    return dataset.map(
        tokenize_batch,
        batched=True,
        remove_columns=dataset.column_names,
        num_proc=num_proc if num_proc > 1 else None,
    )


def collate_batch(tokenizer: AutoTokenizer, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
    batch = tokenizer.pad(features, padding=True, return_tensors="pt")
    labels = batch["input_ids"].clone()
    labels[batch["attention_mask"] == 0] = -100
    batch["labels"] = labels
    return batch


def evaluate_model(
    model_path: str,
    tokenizer: AutoTokenizer,
    dataset: Any,
    args: argparse.Namespace,
) -> Dict[str, float]:
    dtype = choose_dtype()
    model_kwargs: Dict[str, Any] = {
        "dtype": dtype,
        "low_cpu_mem_usage": True,
        "trust_remote_code": args.trust_remote_code,
    }
    if args.device == "auto":
        model_kwargs["device_map"] = "auto"

    model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)
    if args.resize_token_embeddings:
        model.resize_token_embeddings(len(tokenizer))
    model.eval()

    if args.device in {"cuda", "cpu"}:
        device = torch.device(args.device)
        model.to(device)
    else:
        device = model.device

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=lambda feats: collate_batch(tokenizer, feats),
    )

    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(**batch)
            loss = outputs.loss
            token_count = (batch["labels"] != -100).sum().item()
            total_loss += loss.item() * token_count
            total_tokens += token_count

    avg_loss = total_loss / max(total_tokens, 1)
    try:
        ppl = math.exp(avg_loss)
    except OverflowError:
        ppl = float("inf")
    return {"loss": avg_loss, "perplexity": ppl}


def main() -> None:
    args = parse_args()

    dataset = load_text_dataset(args.data, args.split)
    if args.limit:
        dataset = dataset.select(range(args.limit))

    for model_path in args.model:
        tokenizer_path = args.tokenizer if args.tokenizer else model_path
        tokenizer = build_tokenizer(
            tokenizer_path=tokenizer_path,
            fix_mistral_regex=args.fix_mistral_regex,
            trust_remote_code=args.trust_remote_code,
        )
        tokenizer.model_max_length = args.max_length

        tokenized = tokenize_dataset(
            dataset=dataset,
            tokenizer=tokenizer,
            text_field=args.dataset_field,
            max_length=args.max_length,
            add_eos=args.add_eos,
            num_proc=args.num_proc,
        )
        tokenized.set_format(type="torch")

        results = evaluate_model(
            model_path=model_path,
            tokenizer=tokenizer,
            dataset=tokenized,
            args=args,
        )
        print(f"Model: {model_path}")
        print(f"  loss: {results['loss']:.6f}")
        print(f"  ppl:  {results['perplexity']:.4f}")


if __name__ == "__main__":
    main()
