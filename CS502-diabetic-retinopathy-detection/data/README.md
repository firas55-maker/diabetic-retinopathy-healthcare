# Dataset — Diabetic Retinopathy

This directory contains the retinal fundus image dataset used for training and evaluating the diabetic retinopathy detection models in this project.

> **Important:** The dataset is **not stored in this Git repository** because of its size and the licensing/usage conditions of the underlying datasets. Only this documentation file is tracked by Git.

---

## 1. Dataset Overview

The project uses the publicly available **Eyepacs, Aptos, Messidor Diabetic Retinopathy** dataset, which combines retinal fundus images from multiple diabetic retinopathy datasets:

* **EyePACS**
* **APTOS**
* **APTOS — Gaussian Filtered**
* **Messidor**

The original unified dataset contains:

| Property               | Value                                        |
| ---------------------- | -------------------------------------------- |
| Total images           | **92,501 JPG images**                        |
| Image type             | Retinal fundus photographs                   |
| Original split         | **80% Train / 10% Validation / 10% Test**    |
| Approximate local size | **~3–4 GB**                                  |
| Task                   | Diabetic retinopathy severity classification |

The dataset provides images representing different levels of diabetic retinopathy, enabling the development and evaluation of computer-vision models for retinal screening.

The dataset's official Kaggle page describes the original 92,501-image version and its 80/10/10 random split.

---

## 2. Dataset Download

### Recommended download source

Download the dataset from its original Kaggle repository:

**Eyepacs, Aptos, Messidor Diabetic Retinopathy**

[Download dataset from Kaggle](https://www.kaggle.com/datasets/ascanipek/eyepacs-aptos-messidor-diabetic-retinopathy?utm_source=chatgpt.com)

You may need to sign in to Kaggle before downloading.

### Alternative source: APTOS 2019

The APTOS component is also available through the official APTOS 2019 Kaggle competition:

[APTOS 2019 Blindness Detection — Kaggle](https://www.kaggle.com/competitions/aptos2019-blindness-detection/data?utm_source=chatgpt.com)

The APTOS competition dataset contains retinal fundus photographs graded from 0 to 4 according to diabetic retinopathy severity.

---

## 3. Expected Directory

After downloading the dataset, place it inside the computer-vision project:

```text
CS502-diabetic-retinopathy-detection/
└── data/
    ├── train/
    ├── validation/
    ├── test/
    └── ...
```

> The exact directory structure should match the paths expected by the project's data-loading code and notebooks.

The complete dataset should remain local and should **not** be committed to GitHub.

---

## 4. Dataset Split

The original unified dataset was randomly divided into:

```text
Training      80%
Validation    10%
Testing       10%
```

This separation is used to support:

* Model training
* Hyperparameter/model selection
* Final model evaluation on unseen images

The project should preserve the separation between training, validation, and test data to reduce the risk of data leakage.

---

## 5. Image Preprocessing

The dataset contains retinal fundus photographs collected from different sources and therefore includes variation in:

* Image quality
* Illumination
* Camera characteristics
* Field of view
* Retinal appearance
* Acquisition conditions

The dataset release also provides processed/augmented variants. The dataset authors describe a later version in which images were resized to **600 × 600 pixels** and manually augmented, increasing the collection to **143,669 images**.

For this project, preprocessing and image transformations are handled by the computer-vision pipeline contained in:

```text
CS502-diabetic-retinopathy-detection/
```

Refer to the notebooks and source code there for the exact preprocessing pipeline used during experiments.

---

## 6. Diabetic Retinopathy Classes

The dataset uses five diabetic retinopathy severity grades:

| Grade | Description                        |
| ----: | ---------------------------------- |
| **0** | No diabetic retinopathy            |
| **1** | Mild diabetic retinopathy          |
| **2** | Moderate diabetic retinopathy      |
| **3** | Severe diabetic retinopathy        |
| **4** | Proliferative diabetic retinopathy |

These five grades are commonly used for diabetic retinopathy severity classification in the APTOS dataset.

---

## 7. Why Multiple Datasets Were Combined

Combining images from multiple retinal datasets provides greater variation in:

* Patient populations
* Imaging devices
* Image quality
* Acquisition conditions
* Retinal characteristics

This diversity is useful for developing computer-vision models intended to generalize beyond a single image source.

However, differences between datasets can also introduce **domain shift**, differences in annotation practices, and other sources of bias. Model performance should therefore be interpreted in the context of the datasets used for training and evaluation.

---

## 8. Reproducibility

This Git repository contains the project source code required to reproduce the computer-vision pipeline, including:

```text
Model architectures
Data loading
Preprocessing
Training
Validation
Testing
Evaluation
Inference
Grad-CAM / visual explanations
```

To reproduce the experiments:

1. Clone the repository.
2. Obtain the dataset from the source above.
3. Place the dataset under:

```text
CS502-diabetic-retinopathy-detection/data/
```

4. Install the required Python dependencies.
5. Follow the relevant notebooks/scripts in the computer-vision project.
6. Run training or inference according to the project documentation.

---

## 9. Data Privacy and Licensing

The dataset consists of publicly distributed research data originating from multiple retinal-image datasets.

The dataset itself is **not redistributed by this repository**.

Users are responsible for reviewing and complying with the current terms, licenses, competition rules, and usage conditions of the original dataset providers before downloading or redistributing the data.

For the Kaggle unified dataset, refer to the dataset page for the current licensing and usage information:

[Kaggle dataset page](https://www.kaggle.com/datasets/ascanipek/eyepacs-aptos-messidor-diabetic-retinopathy?utm_source=chatgpt.com)

For APTOS 2019:

[APTOS 2019 dataset and competition rules](https://www.kaggle.com/competitions/aptos2019-blindness-detection?utm_source=chatgpt.com)

For EyePACS information and research-data access:

[EyePACS Data & Research Information](https://www.eyepacs.com/data-analysis?utm_source=chatgpt.com)

---

## 10. Citation

If you use the unified dataset, please cite the original Kaggle dataset:

> Canipek, A. S., Çakan, M., & Aktuğ, A. (2024). *Eyepacs, Aptos, Messidor Diabetic Retinopathy*. Kaggle.

Dataset:

[https://www.kaggle.com/datasets/ascanipek/eyepacs-aptos-messidor-diabetic-retinopathy](https://www.kaggle.com/datasets/ascanipek/eyepacs-aptos-messidor-diabetic-retinopathy?utm_source=chatgpt.com)

---

## 11. Repository Policy

The following files should **not** be committed to Git:

```text
*.jpg
*.jpeg
*.png
*.zip
*.tar
*.tar.gz
```

The full dataset is intentionally excluded from version control because of its size.

This repository tracks the **code, configuration, documentation, model architecture, notebooks, and reproducibility instructions**, while the dataset remains available through its original distribution source.
