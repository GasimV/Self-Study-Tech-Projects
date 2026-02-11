import json
import os
import urllib
import torch
from torch.utils.data import Dataset


# Alpaca style
def format_input(entry):
    instruction_text = (
        f"Below is an instruction that describes a task. "
        f"Write a response that appropriately completes the request."
        f"\n\n### Instruction:\n{entry['instruction']}"
    )

    input_text = (
        f"\n\n### Input:\n{entry['input']}" if entry["input"] else ""
    )
    return instruction_text + input_text


def split_data(data, train_ratio=0.85, test_ratio=0.10, verbose=False):
    """
    Split data into training, testing, and validation sets.

    Args:
        data (sequence): Dataset to split
        train_ratio (float): Proportion of data for training
        test_ratio (float): Proportion of data for testing

    Returns:
        tuple: (train_data, val_data, test_data)
    """
    if train_ratio + test_ratio >= 1.0:
        raise ValueError("train_ratio + test_ratio must be less than 1")

    train_portion = int(len(data) * train_ratio)
    test_portion = int(len(data) * test_ratio)

    train_data = data[:train_portion]
    test_data = data[train_portion:train_portion + test_portion]
    val_data = data[train_portion + test_portion:]

    if verbose:
        print(f"Training set length: {len(train_data)}")
        print(f"Validation set length: {len(val_data)}")
        print(f"Test set length: {len(test_data)}")

    return train_data, val_data, test_data

# Example usage:
# train_data, val_data, test_data = split_data(data)
# train_data, val_data, test_data = split_data(data, verbose=True)


class InstructionDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.encoded_texts = []
        for entry in data:         #1 Pretokenizes texts
            instruction_plus_input = format_input(entry)
            response_text = f"\n\n### Response:\n{entry['output']}"
            full_text = instruction_plus_input + response_text
            self.encoded_texts.append(
                tokenizer.encode(full_text)
            )

    def __getitem__(self, index):
        return self.encoded_texts[index]

    def __len__(self):
        return len(self.data)


def custom_collate_fn(
    batch,
    pad_token_id=50256,
    ignore_index=-100,
    allowed_max_length=None,
    device="cpu"
):
    batch_max_length = max(len(item)+1 for item in batch)
    inputs_lst, targets_lst = [], []

    for item in batch:
        new_item = item.copy()
        new_item += [pad_token_id]


        padded = (                               #1 Pads sequences to max_length
            new_item + [pad_token_id] *          #1
            (batch_max_length - len(new_item))   #1
        )
        inputs = torch.tensor(padded[:-1])      #2 Truncates the last token for inputs
        targets = torch.tensor(padded[1:])     #3 Shifts +1 to the right for targets

        mask = targets == pad_token_id              #4 Replaces all but the first padding tokens in targets by ignore_index
        indices = torch.nonzero(mask).squeeze()     #4
        if indices.numel() > 1:                     #4
            targets[indices[1:]] = ignore_index     #4

        if allowed_max_length is not None:
            inputs = inputs[:allowed_max_length]       #5 Optionally truncates to the maximum sequence length
            targets = targets[:allowed_max_length]     #5

        inputs_lst.append(inputs)
        targets_lst.append(targets)

    inputs_tensor = torch.stack(inputs_lst).to(device)
    targets_tensor = torch.stack(targets_lst).to(device)
    return inputs_tensor, targets_tensor


