import torch
import json
import os
import torch.optim as optim
import pathlib

from ..Fast_RCNN.ObjectDetector import ImageObjectDetector
from ..Fast_RCNN.model import CustomFasterRCNN


def load_model(checkpoint_path, model, optimizer):
    """
    Load the model and optimizer state from a checkpoint file and ensure they are moved to the specified device.
    """
    print("path: " + checkpoint_path)
    if os.path.isfile(checkpoint_path):
        # Add map_location to ensure the checkpoint is loaded to the correct device
        # checkpoint = torch.load(checkpoint_path, map_location=device)
        checkpoint = torch.load(checkpoint_path, map_location=torch.device("cpu"))

        # Load the model state
        model.load_state_dict(checkpoint["model_state_dict"])

        # Load the optimizer state
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        # Ensure optimizer's stored states are on the right device
        for state in optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    # state[k] = v.to(device)
                    state[k] = v

        # Load other information
        # epoch = checkpoint['epoch']
        # print(f"Checkpoint loaded from {checkpoint_path} at epoch {epoch + 1}")
    else:
        print("No checkpoint found at specified path!")

    return model  # , optimizer, epoch


def rcnn_model(img):
    # Load label map
    path = pathlib.Path(__file__).parent.resolve()
    label_map_file_path = f"{path}/label_map_fridgeapp.json"
    with open(label_map_file_path, "r") as f:
        loaded_label_map = json.load(f)

    best_checkpoint_path = f"{path}/checkpoint_47.pth"
    # device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    device = None
    model = CustomFasterRCNN()
    optimizer = optim.SGD(
        model.parameters(), lr=0.005, momentum=0.9, weight_decay=0.0005
    )
    best_model = load_model(best_checkpoint_path, model, optimizer)

    detector = ImageObjectDetector(
        model=best_model, label_map=loaded_label_map, device=device
    )

    high_confidence_labels, image_with_boxes = detector.detect_and_draw_boxes(
        image_path=img
    )

    return {"ingredients": high_confidence_labels, "image": image_with_boxes}
