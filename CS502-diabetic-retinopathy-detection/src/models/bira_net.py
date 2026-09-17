import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.cuda
import torchvision.transforms as transforms
import torch.nn.functional as F
from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights


class Lambda(nn.Module):
    def __init__(self, lambd):
        super(Lambda, self).__init__()
        self.lambd = lambd

    def forward(self, x):
        return self.lambd(x)


class BiraNet(nn.Module):
    """
    BiraNet model. With EfficientNet-B3 as backbone.
    Source: https://github.com/ISS-Kerui/BIRA-NET-BILINEAR-ATTENTION-NET-FOR-DIABETIC-RETINOPATHY-GRADING
    """

    def __init__(self, classes_num):
        super(BiraNet, self).__init__()
        MODEL = "results/models/eff_net_400x400.pt"  # Load the pretrained model
        weights = EfficientNet_B3_Weights.DEFAULT
        effNet = efficientnet_b3(weights=weights)
        effNet.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(in_features=1536, out_features=5, bias=True),
        )

        try:
            model_state_dict = torch.load(
                MODEL, map_location=lambda storage, loc: storage
            )
            effNet.load_state_dict(model_state_dict)
        except RuntimeError as e:
            print("Error loading the model:", e)

        # freeze
        for param in effNet.parameters():
            param.requires_grad = False

        effNet = list(effNet.children())[:-1]
        self.features = nn.Sequential(*effNet)

        self.attention = nn.Sequential(
            nn.BatchNorm2d(1536),
            nn.Conv2d(1536, 64, kernel_size=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(64, 16, kernel_size=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(16, 8, kernel_size=1, padding=0),
            nn.ReLU(),
            nn.Conv2d(8, 1, kernel_size=1, padding=0),
            nn.Sigmoid(),
        )
        self.up_c2 = nn.Conv2d(1, 1536, kernel_size=1, padding=0, bias=False)
        nn.init.constant_(self.up_c2.weight, 1)
        self.denses = nn.Sequential(
            nn.Linear(1536, 256), nn.Dropout(0.5), nn.Linear(256, classes_num)
        )

    def forward(self, x):
        x = self.features(x)

        atten_layers = self.attention(x)
        atten_layers = self.up_c2(atten_layers)
        # Print atten_layers.shape
        mask_features = torch.matmul(atten_layers, x)
        # Print mask_features.shape
        gap_features = F.avg_pool2d(mask_features, kernel_size=mask_features.size()[2:])
        # Print gap_features.shape
        gap_mask = F.avg_pool2d(atten_layers, kernel_size=atten_layers.size()[2:])
        # Print gap_mask.shape
        gap = torch.squeeze(Lambda(lambda x: x[0] / x[1])([gap_features, gap_mask]))
        # Print gap.shape
        x = self.denses(gap)
        return F.log_softmax(x, dim=1)
