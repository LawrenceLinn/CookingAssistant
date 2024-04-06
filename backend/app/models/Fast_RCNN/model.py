import torch
import torch.nn as nn
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


class CustomTwoMLPHead(nn.Module):
    def __init__(self, in_channels, representation_size):
        super(CustomTwoMLPHead, self).__init__()
        self.fc6 = nn.Linear(in_channels, 4096)
        self.fc7 = nn.Linear(4096, 2048)
        self.fc8 = nn.Linear(2048, representation_size)

    def forward(self, x):
        x = x.flatten(start_dim=1)
        x = nn.functional.relu(self.fc6(x))
        x = nn.functional.relu(self.fc7(x))
        x = nn.functional.relu(self.fc8(x))
        return x


class CustomFasterRCNN(torch.nn.Module):
    def __init__(self, num_classes=73):
        super(CustomFasterRCNN, self).__init__()
        self.model = torchvision.models.detection.fasterrcnn_resnet50_fpn(
            weights=torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        )
        in_channels = 12544
        representation_size = 1024

        self.model.roi_heads.box_head = CustomTwoMLPHead(
            in_channels=in_channels, representation_size=representation_size
        )

        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    def forward(self, images, targets=None):
        return self.model(images, targets)
