"""
Trims images to remove any black space around the retina, ensuring that the retina is not cropped. 
Than resizes the images to 512x512 pixels while keeping the aspect ratio.
"""

import os
import subprocess
import numpy as np
from PIL import Image
import warnings
from multiprocessing import Pool
from tqdm import tqdm
import cv2


def extract_zip_files(zip_file_path: str, output_dir: str):
    """
    Extracts the zip files into the output directory.
    Args:
        zip_file_path: Path to the first part of the zip file.
        output_dir: Directory to extract the zip files.
    """

    subprocess.run(["7z", "x", zip_file_path, f"-o{output_dir}", "-y"])


def trim(image):
    """
    Trims the black part of the image around the retina.
    """
    percentage = 0.02
    threshold = 0.1

    # convert the image to grayscale
    img = np.array(image)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # compute the binary matrix of the pixels that are above a certain threshold
    image = img_gray > threshold * np.mean(img_gray[img_gray != 0])

    # find the rows and columns where a certain percetage of the pixels are above the threshold
    row_sums = np.sum(image, axis=1)
    col_sums = np.sum(image, axis=0)
    rows = np.where(row_sums > img.shape[1] * percentage)[0]
    cols = np.where(col_sums > img.shape[0] * percentage)[0]
    # take the min and max of the rows and columns to crop the image
    min_row, min_col = np.min(rows), np.min(cols)
    max_row, max_col = np.max(rows), np.max(cols)

    image_crop = img[min_row : max_row + 1, min_col : max_col + 1]
    return Image.fromarray(image_crop)


def resize_maintain_aspect(image, desired_size):
    """
    Adjusts the image size while maintaining the aspect ratio.
    """
    original_size = image.size
    ratio = float(desired_size) / max(original_size)

    new_size = tuple([int(x * ratio) for x in original_size])
    img = image.resize(new_size, Image.ANTIALIAS)

    new_img = Image.new("RGB", (desired_size, desired_size))
    new_img.paste(
        img, ((desired_size - new_size[0]) // 2, (desired_size - new_size[1]) // 2)
    )
    return new_img


def save_single(args):
    """
    Trims and resizes a single image.
    """
    img_file, input_path_folder, output_path_folder, output_size = args
    image_original = Image.open(os.path.join(input_path_folder, img_file))
    # trim and resize the image
    image = trim(image_original)
    image = resize_maintain_aspect(image, desired_size=output_size[0])
    image.save(os.path.join(output_path_folder + img_file))


def fast_image_resize(input_path_folder, output_path_folder, output_size=None):
    """
    Resizes all images in input_path_folder and saves them in output_path_folder.
    """

    # create the output folder if it doesn't exist
    if not os.path.exists(output_path_folder):
        os.makedirs(output_path_folder)

    # create a list of jobs
    jobs = [
        (file, input_path_folder, output_path_folder, output_size)
        for file in os.listdir(input_path_folder)
    ]

    # run the jobs
    with Pool() as p:
        list(tqdm(p.imap_unordered(save_single, jobs), total=len(jobs)))


if __name__ == "__main__":
    zip_file_directory = "/diabetic-retinopathy-detection"
    input_directory = "../original/"
    output_directory = "../resized_optimized/"
    zip_file_path = os.path.join(zip_file_directory, "train.zip.001")

    output_size = (512, 512)

    if os.path.exists(zip_file_path):
        extract_zip_files(zip_file_path, input_directory)

    fast_image_resize(input_directory, output_directory, output_size)
    print("Image trimming and resizing complete.")
