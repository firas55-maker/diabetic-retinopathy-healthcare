import torch
import torch.nn as nn


class SiameseNetwork(nn.Module):
    """
    Siamese Network model. With EfficientNet-B3 as backbone. Can be used with any other model.
    """

    def __init__(self, model, classifier):
        super(SiameseNetwork, self).__init__()
        self.branch = model  # Pre-trained model, e.g. EfficientNet-B3
        self.classifier = classifier

        # Initialize learnable weights
        self.primary_weight = nn.Parameter(torch.tensor(1.0))
        self.secondary_weight = nn.Parameter(torch.tensor(0.0))

    def forward(self, left_eye, right_eye):
        # Extract features for both eyes
        left_features = self.branch(left_eye)
        right_features = self.branch(right_eye)

        # Apply learnable weights
        combined_left = torch.cat(
            (
                left_features * self.primary_weight,
                right_features * self.secondary_weight,
            ),
            1,
        )
        combined_right = torch.cat(
            (
                right_features * self.primary_weight,
                left_features * self.secondary_weight,
            ),
            1,
        )

        # Predictions for both combinations
        prediction_primary = self.classifier(combined_left)
        prediction_secondary = self.classifier(combined_right)

        return prediction_primary, prediction_secondary
