import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Severity grades for diabetic retinopathy (0-4 scale)
SEVERITY_GRADES = {
    0: "No DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR"
}

# ============================================================================
# SIAMESE NETWORK MODEL ARCHITECTURE (from CS502 project)
# ============================================================================

class SiameseNetwork(nn.Module):
    """
    Siamese Network model with EfficientNet-B3 as backbone.
    Processes left and right eye images for DR severity classification.
    """

    def __init__(self, model, classifier):
        super(SiameseNetwork, self).__init__()
        self.branch = model  # Pre-trained EfficientNet-B3 backbone
        self.classifier = classifier

        # Initialize learnable weights for combining features
        self.primary_weight = nn.Parameter(torch.tensor(1.0))
        self.secondary_weight = nn.Parameter(torch.tensor(0.0))

    def forward(self, left_eye, right_eye):
        """
        Forward pass for Siamese network.

        Args:
            left_eye: Left eye image tensor
            right_eye: Right eye image tensor

        Returns:
            Tuple of (primary_prediction, secondary_prediction)
        """
        # Extract features for both eyes
        left_features = self.branch(left_eye)
        right_features = self.branch(right_eye)

        # Apply learnable weights for feature combination
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


# ============================================================================
# SIAMESE NETWORK PREDICTOR
# ============================================================================

class SiamesePredictor:
    """
    Predictor for diabetic retinopathy severity using trained Siamese Network.
    Loads real pretrained weights and performs inference on retinal images.
    """

    def __init__(self, model_path: str, device: str = None):
        """
        Initialize predictor with real trained model.

        Args:
            model_path: Path to pretrained siamese_net_400x400_2.pt weights
            device: 'cuda' or 'cpu'
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = self._get_transforms()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights not found at {model_path}")

        logger.info(f"Using device: {self.device}")
        self.load_model(model_path)

    def _get_transforms(self):
        """
        Get image transformation pipeline matching CS502 project preprocessing.

        - Resize to 400x400 (matching training)
        - Normalize with computed mean/std from training dataset
        - No augmentation for inference (just resize + normalize)
        """
        # Mean and std computed on the training dataset
        mean = [0.4433, 0.3067, 0.2192]
        std = [0.2747, 0.2011, 0.1682]

        return transforms.Compose([
            transforms.Resize((400, 400)),  # 400x400 for Siamese Network
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])

    def load_model(self, model_path: str):
        """
        Load pretrained Siamese Network model with EfficientNet-B3 backbone.

        This reconstructs the full model architecture and loads the saved weights.
        """
        try:
            # Import EfficientNet-B3 from torchvision
            from torchvision.models import efficientnet_b3, EfficientNet_B3_Weights

            logger.info("Loading EfficientNet-B3 backbone...")

            # Load pretrained EfficientNet-B3 with default weights
            backbone = efficientnet_b3(weights=EfficientNet_B3_Weights.DEFAULT)

            # Freeze all backbone parameters (we only train the classifier)
            for param in backbone.parameters():
                param.requires_grad = False

            # Replace the classifier with Identity to extract features
            backbone.classifier = nn.Identity()

            # Create classifier head for 5 DR severity classes
            # Matches the exact architecture from siamese_net.ipynb
            # Takes 2x1536 (left+right features) = 3072 dims
            classifier = nn.Sequential(
                nn.BatchNorm1d(1536 * 2),
                nn.Linear(1536 * 2, 500),
                nn.BatchNorm1d(500),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(500, 100),
                nn.BatchNorm1d(100),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(100, 5)  # 5 classes: No DR, Mild, Moderate, Severe, Proliferative
            )

            # Construct Siamese Network
            self.model = SiameseNetwork(backbone, classifier)

            # Load pretrained weights
            logger.info(f"Loading pretrained weights from {model_path}...")
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)

            # Move to device and set to eval mode
            self.model.to(self.device)
            self.model.eval()

            logger.info(f"Model loaded successfully from {model_path}")
            logger.info(f"Model device: {self.device}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Cannot initialize Siamese Network: {e}")

    def predict(self, image_path: str) -> Tuple[int, float]:
        """
        Predict DR severity from single retinal image.

        For a single image, we duplicate it (left_eye = right_eye = same image)
        and average the two predictions from the Siamese network.

        Args:
            image_path: Path to retinal fundus image

        Returns:
            Tuple of (grade: int 0-4, confidence: float 0-1)
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            # For single image inference, duplicate the image for both branches
            # This mirrors the training setup where we have left/right eye pairs
            left_eye = image_tensor
            right_eye = image_tensor

            # Inference with no gradient computation
            with torch.no_grad():
                # Forward pass through Siamese network
                prediction_primary, prediction_secondary = self.model(left_eye, right_eye)

                # Average predictions from both branches
                avg_prediction = (prediction_primary + prediction_secondary) / 2

                # Get probabilities via softmax
                probabilities = torch.softmax(avg_prediction, dim=1)

                # Get max confidence and predicted class
                confidence, predicted = torch.max(probabilities, 1)

                # Convert to Python values
                grade = int(predicted.cpu().numpy()[0])
                confidence = float(confidence.cpu().numpy()[0])

                logger.info(f"Prediction: Grade={grade} ({SEVERITY_GRADES[grade]}), Confidence={confidence:.4f}")

                return grade, confidence

        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise RuntimeError(f"Prediction failed: {e}")


# ============================================================================
# GLOBAL PREDICTOR INSTANCE & API
# ============================================================================

_predictor: Optional[SiamesePredictor] = None


def get_predictor(model_path: str = None) -> SiamesePredictor:
    """
    Get or create global predictor instance.

    Args:
        model_path: Path to pretrained model weights

    Returns:
        SiamesePredictor instance
    """
    global _predictor
    if _predictor is None:
        if model_path is None:
            # Use default path relative to this file
            default_path = Path(__file__).parent / "ml_models" / "siamese_net_400x400_2.pt"
            model_path = str(default_path)

        logger.info(f"Initializing Siamese Network predictor with model: {model_path}")
        _predictor = SiamesePredictor(model_path=model_path)
    return _predictor


def predict(image_path: str, model_path: str = None) -> Dict[str, any]:
    """
    Predict DR severity from retinal fundus image using trained Siamese Network.

    Args:
        image_path: Path to retinal fundus image file
        model_path: Optional path to model weights (uses default if None)

    Returns:
        Dictionary with:
            - grade: int (0-4, DR severity grade)
            - severity: str (human-readable severity label)
            - confidence: float (0-1, model confidence in prediction)

    Raises:
        FileNotFoundError: If model weights file not found
        RuntimeError: If inference fails
    """
    try:
        predictor = get_predictor(model_path)
        grade, confidence = predictor.predict(image_path)

        return {
            "grade": grade,
            "severity": SEVERITY_GRADES.get(grade, "Unknown"),
            "confidence": round(confidence, 4)
        }
    except Exception as e:
        logger.error(f"Prediction error for {image_path}: {e}")
        raise
