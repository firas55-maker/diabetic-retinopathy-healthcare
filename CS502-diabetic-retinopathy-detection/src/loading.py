import os
import pandas as pd
import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader, random_split
from torch.utils.data.sampler import WeightedRandomSampler
from torchvision import transforms
from sklearn.model_selection import train_test_split


class TrainDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None, file_extension=".jpeg"):
        # dataframe: pandas dataframe with image names and labels
        self.dataframe = dataframe
        # img_dir: directory with images
        self.img_dir = img_dir
        # transform: transformations to be applied to the images
        self.transform = transform
        # file_extension: extension of the images (default: .jpeg)
        self.file_extension = file_extension

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        # Get image name and label
        img_name = self.dataframe.iloc[idx, 0] + self.file_extension
        # Get image path
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path)
        # Get image label
        label = self.dataframe.iloc[idx, 1]
        # Apply transformations
        if self.transform:
            image = self.transform(image)

        return image, label


class TestDataset(Dataset):
    def __init__(self, img_dir, transform=None, file_extension=".jpg"):
        # img_dir: directory with images
        self.transform = transform
        # transform: transformations to be applied to the images
        self.img_dir = img_dir
        # file_extension: extension of the images (default: .jpeg)
        self.file_extension = file_extension
        # Get image names, sorted
        self.image_files = sorted(
            [f for f in os.listdir(img_dir) if f.endswith(file_extension)]
        )

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        # Get image name
        img_name = self.image_files[idx]
        # Get image path
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path)
        # Apply transformations
        if self.transform:
            image = self.transform(image)

        # Remove the file extension to get the base name
        base_name = img_name.rsplit(".", 1)[0]
        return image, base_name


def undersample_weights(labels):
    # Calculate weights for weighted random sampler
    class_counts = np.bincount(labels)
    # Inverse of the class counts
    class_weights = 1.0 / class_counts
    # Weights for each sample, with respect to the class
    weights = class_weights[labels]
    return torch.DoubleTensor(weights)


def load_data(labels_dir, img_dir, img_size, batch_size):
    # Mean, std calculated on the train dataset
    mean = [0.4433, 0.3067, 0.2192]
    std = [0.2747, 0.2011, 0.1682]

    # Transformations for the training dataset
    train_transform = transforms.Compose(
        [
            transforms.Resize(img_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )

    # Transformations for the validation dataset
    val_transform = transforms.Compose(
        [
            transforms.Resize(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )

    full_dataset = pd.read_csv(labels_dir)

    # Implicitly val is 0.09
    train_size = 0.91

    num_samples = len(full_dataset)
    num_train = int(train_size * num_samples)
    num_val = num_samples - num_train
    print("Number of train samples:" + str(num_train))
    print("Number of validation samples:" + str(num_val))

    # Data split, train and validaton
    train_df, val_df = train_test_split(
        full_dataset, train_size=num_train, shuffle=False
    )

    train_dataset = TrainDataset(
        dataframe=train_df, img_dir=img_dir, transform=train_transform
    )
    val_dataset = TrainDataset(
        dataframe=val_df, img_dir=img_dir, transform=val_transform
    )

    # Calculate sample weights for weighted random sampler
    train_labels = train_dataset.dataframe.iloc[:, 1].values
    sample_weights = undersample_weights(train_labels)

    # WeightedRandomSampler for undersampling
    weighted_sampler = WeightedRandomSampler(
        weights=sample_weights, num_samples=len(sample_weights), replacement=True
    )

    # Data loaders
    # shuffle = False for siamese network
    # sampler = weighted_sampler for undersampling
    train_data_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)

    val_data_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    return train_data_loader, val_data_loader


def load_test_data(img_dir, img_size, batch_size):
    # Mean, std calculated on the train dataset
    mean = [0.4433, 0.3067, 0.2192]
    std = [0.2747, 0.2011, 0.1682]

    # Transformations for the test dataset
    transform = transforms.Compose(
        [
            transforms.Resize(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )

    test_dataset = TestDataset(img_dir=img_dir, transform=transform)
    test = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return test
