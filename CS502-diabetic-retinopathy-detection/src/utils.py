import torch
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    cohen_kappa_score,
)


def calculate_metrics(labels, preds):
    """
    Calculate accuracy, precision, recall, kappa and f1_score.
    Args:
        labels: list of labels
        preds: list of predictions
    Returns:
        metrics: dictionary with metrics
    """
    acc = accuracy_score(labels, preds)
    precision = precision_score(labels, preds, average="macro")
    recall = recall_score(labels, preds, average="macro")
    kappa = cohen_kappa_score(labels, preds, weights="quadratic")
    f1 = f1_score(labels, preds, average="macro")

    metrics = {
        "accuracy": acc,
        "quadratic_kappa": kappa,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }

    return metrics


def seed_everything(seed=128):
    """Function for setting seeds."""
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)


def imshow(img, label):
    """
    Function to show an image without axes and with a label.
    Args:
        img: image to visualize
        label: label of the image
    """
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.title(f"Label: {label}")
    plt.axis("off")
    plt.show()


# Sourced from: https://www.binarystudy.com/2022/04/how-to-normalize-image-dataset-inpytorch.html
def batch_mean_and_sd(loader):
    """
    Calculate mean and std of dataset for normalization.
    Args:
        loader: data loader
    Returns:
        mean: mean of the dataset
        std: std of the dataset
    """
    cnt = 0
    fst_moment = torch.empty(3)
    snd_moment = torch.empty(3)

    for images, _ in loader:
        b, c, h, w = images.shape
        nb_pixels = b * h * w
        sum_ = torch.sum(images, dim=[0, 2, 3])
        sum_of_square = torch.sum(images**2, dim=[0, 2, 3])
        fst_moment = (cnt * fst_moment + sum_) / (cnt + nb_pixels)
        snd_moment = (cnt * snd_moment + sum_of_square) / (cnt + nb_pixels)
        cnt += nb_pixels

    mean, std = fst_moment, torch.sqrt(snd_moment - fst_moment**2)
    return mean, std
