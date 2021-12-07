import torch
import torch.nn as nn
import torchvision

from .binarized_modules import BinarizeLinear

# Constants
IMAGE_WIDTH = 32
IMAGE_HEIGHT = 32
COLOR_CHANNELS = 3
EPOCHS = 300
LEARNING_RATES = [.00001, 0.0001, 0.001, 0.01, 0.1]
KEEP_RATES = [.5, .65, .8]
MOMENTUM_RATES = [.25, .5, .75]
WEIGHT_DECAY_RATES = [.0005, .005, .05]
CLASSES = ['plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
N_CLASSES = len(CLASSES)

class CifarMLP(torch.nn.Module):
    def __init__(self, n_hidden_nodes, **kwargs):
        super().__init__()
        # Set up perceptron layers and add dropout
        self.classifier = nn.Sequential(
            BinarizeLinear(IMAGE_WIDTH * IMAGE_WIDTH * COLOR_CHANNELS, 4096),
            nn.BatchNorm1d(4096),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(4096, 4096),
            nn.BatchNorm1d(4096),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(4096, 256),
            nn.BatchNorm1d(256),
            nn.Hardtanh(inplace=True),
            BinarizeLinear(256, 16),
            nn.Hardtanh(inplace=True),
            BinarizeLinear(16, 16),
            nn.Hardtanh(inplace=True),
            BinarizeLinear(16, N_CLASSES),
            nn.BatchNorm1d(N_CLASSES),
            nn.LogSoftmax()
        )


    def forward(self, x):
        x = x.reshape(-1, IMAGE_WIDTH * IMAGE_WIDTH * COLOR_CHANNELS)
        return self.classifier(x)

def cifar_mlp(*args, **kwargs):
    return CifarMLP(256, *args, **kwargs)