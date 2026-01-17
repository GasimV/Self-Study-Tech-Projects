import torch


def save_model_state(model, path): # path could be, for example, "model.pth"
    torch.save(model.state_dict(), path)


def load_model_state(model, path, device=None):
    map_location = device if device is not None else "cpu"
    state_dict = torch.load(path, map_location=map_location)
    model.load_state_dict(state_dict)
    return model


def save_checkpoint(model, optimizer, path):
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        },
        path, # e.g., "model_and_optimizer.pth"
    )


def load_checkpoint(model, optimizer, path, device=None):
    map_location = device if device is not None else "cpu"
    checkpoint = torch.load(path, map_location=map_location)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return model, optimizer
