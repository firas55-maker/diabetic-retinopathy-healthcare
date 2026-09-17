from tqdm import tqdm
from src.utils import calculate_metrics
import torch
import torch.nn as nn


def train(
    model,
    train_loader,
    validation_loader,
    criterion,
    optimizer,
    device,
    model_name,
    num_epochs=20,
):
    best_kappa_score = 0.0
    for epoch in range(num_epochs):
        model.train()
        train_preds, train_labels = [], []
        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            predicted = outputs.argmax(dim=1)
            train_preds.extend(predicted.cpu().numpy())
            train_labels.extend(labels.cpu().numpy())

        # Calculate metrics
        train_metrics = calculate_metrics(train_labels, train_preds)
        print(f"Epoch: {epoch+1} Loss: {loss.item()}")
        print("Train accuracy: ", train_metrics["accuracy"])
        print("Train kappa score: ", train_metrics["quadratic_kappa"])
        print("---------------")

        model.eval()
        validation_preds, validation_labels = [], []
        for images, labels in tqdm(validation_loader):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            predicted = outputs.argmax(dim=1)
            validation_preds.extend(predicted.cpu().numpy())
            validation_labels.extend(labels.cpu().numpy())

        # Calculate metrics
        validation_metrics = calculate_metrics(validation_labels, validation_preds)
        print("Validation accuracy: ", validation_metrics["accuracy"])
        print("Validation kappa score: ", validation_metrics["quadratic_kappa"])
        print("---------------")

        current_kappa_score = validation_metrics["quadratic_kappa"]
        if current_kappa_score > best_kappa_score:
            best_kappa_score = current_kappa_score
            # Save best model according to kappa score on validation set
            torch.save(model.state_dict(), model_name)
            print(f"New best model saved with kappa score: {best_kappa_score}")


def train_siamese(
    siamese_net,
    train_loader,
    validation_loader,
    criterion,
    optimizer,
    device,
    model_name,
    num_epochs=20,
):
    best_kappa_score = 0.0
    for epoch in range(num_epochs):
        siamese_net.train()
        train_preds, train_labels = [], []
        running_loss = 0.0
        for images, labels in tqdm(train_loader):
            images, labels = images.to(device), labels.to(device)
            left_images = images[::2]  # This will take images 0, 2, 4, 6
            right_images = images[1::2]  # This will take images 1, 3, 5, 7
            left_labels = labels[::2]
            right_labels = labels[1::2]
            optimizer.zero_grad()

            # Forward pass
            outputs_left, outputs_right = siamese_net(left_images, right_images)

            # Compute loss for both outputs
            loss_primary = criterion(outputs_left, left_labels)
            loss_secondary = criterion(outputs_right, right_labels)
            total_loss = (loss_primary + loss_secondary) / 2

            # Backward pass
            total_loss.backward()
            running_loss += total_loss.item()

            # Update weights
            optimizer.step()

            predicted_left = outputs_left.argmax(dim=1)
            predicted_right = outputs_right.argmax(dim=1)

            train_preds.extend(predicted_left.cpu().numpy())
            train_preds.extend(predicted_right.cpu().numpy())
            train_labels.extend(left_labels.cpu().numpy())
            train_labels.extend(right_labels.cpu().numpy())

        # Calculate metrics for the training data
        train_metrics = calculate_metrics(train_labels, train_preds)
        print("Epoch: ", epoch + 1, "Loss: ", running_loss / len(train_loader))
        print("Train accuracy: ", train_metrics["accuracy"])
        print("Train kappa score: ", train_metrics["quadratic_kappa"])
        print("---------------")

        siamese_net.eval()
        validation_preds, validation_labels = [], []
        for images, labels in tqdm(validation_loader):
            images, labels = images.to(device), labels.to(device)
            left_images = images[::2]  # This will take images 0, 2, 4, 6
            right_images = images[1::2]  # This will take images 1, 3, 5, 7
            left_labels = labels[::2]
            right_labels = labels[1::2]

            outputs_left, outputs_right = siamese_net(left_images, right_images)

            loss_primary = criterion(outputs_left, left_labels)
            loss_secondary = criterion(outputs_right, right_labels)
            total_loss = (loss_primary + loss_secondary) / 2

            predicted_left = outputs_left.argmax(dim=1)
            predicted_right = outputs_right.argmax(dim=1)

            validation_preds.extend(predicted_left.cpu().numpy())
            validation_preds.extend(predicted_right.cpu().numpy())
            validation_labels.extend(left_labels.cpu().numpy())
            validation_labels.extend(right_labels.cpu().numpy())

        # Calculate metrics for the validation data
        validation_metrics = calculate_metrics(validation_labels, validation_preds)
        print("Validation accuracy: ", validation_metrics["accuracy"])
        print("Validation kappa score: ", validation_metrics["quadratic_kappa"])
        print("---------------")

        current_kappa_score = validation_metrics["quadratic_kappa"]
        if current_kappa_score > best_kappa_score:
            best_kappa_score = current_kappa_score
            # Save best model according to kappa score on validation set
            torch.save(siamese_net.state_dict(), model_name)
            print(f"New best model saved with kappa score: {best_kappa_score}")
