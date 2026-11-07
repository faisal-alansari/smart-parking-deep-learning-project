"""OccupancyCNN: a small CNN trained from random initialisation."""

import torch
from torch import nn


class OccupancyCNN(nn.Module):
    """Conv blocks (two 3x3 convs, batch norm, ReLU, 2x2 max-pool), global pooling, one logit.

    The output is a logit for "occupied"; apply a sigmoid for the probability.
    """

    def __init__(self, channels: list[int], dropout: float) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        c_in = 3
        for c in channels:
            layers += [
                nn.Conv2d(c_in, c, 3, padding=1, bias=False),
                nn.BatchNorm2d(c),
                nn.ReLU(inplace=True),
                nn.Conv2d(c, c, 3, padding=1, bias=False),
                nn.BatchNorm2d(c),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(2),
            ]
            c_in = c
        self.features = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.Flatten(), nn.Dropout(dropout), nn.Linear(c_in, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = torch.nn.functional.adaptive_avg_pool2d(x, 1)
        return self.head(x).squeeze(1)


def count_parameters(model: nn.Module) -> int:
    """Number of trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
