"""
Resizes the images to a height of 512 pixels while maintaining the aspect ratio and then crops the central 512 pixels of the image.
"""

import os
import subprocess
from PIL import Image


def extract_zip_files(zip_file_path: str, output_dir: str):
    """
    Extracts the zip files into the output directory.
    Args:
        zip_file_path: Path to the first part of the zip file.
        output_dir: Directory to extract the zip files.
    """

    subprocess.run(["7z", "x", zip_file_path, f"-o{output_dir}", "-y"])


def resize_and_crop_image(input_dir: str, output_dir: str):
    """
    Resizes and crops the images from the input directory.
    Args:
        input_dir: Directory containing the images to resize and crop.
        output_dir: Directory to save the resized and cropped images.
    """

    for filename in os.listdir(input_dir):
        if filename.endswith((".jpeg", ".jpg")):
            file_path = os.path.join(input_dir, filename)

            try:
                with Image.open(file_path) as img:
                    # calculate the new width while maintaining the aspect ratio
                    aspect_ratio = img.width / img.height
                    new_width = int(aspect_ratio * 512)

                    # resize the image to have a height of 512 while maintaining aspect ratio
                    img_resized = img.resize((new_width, 512), Image.LANCZOS)

                    # calculate left and right coordinates to crop the central part
                    left = (img_resized.width - 512) / 2
                    right = (img_resized.width + 512) / 2
                    top = 0
                    bottom = 512

                    # crop the central part
                    img_cropped = img_resized.crop((left, top, right, bottom))

                    # save the cropped image to the output directory
                    output_file_path = os.path.join(output_dir, filename)
                    img_cropped.save(output_file_path)

            except IOError as e:
                print(f"Error processing file {filename}: {e}")


if __name__ == "__main__":
    zip_file_directory = "/diabetic-retinopathy-detection"
    input_directory = "/data/original"
    output_directory = "/data/resized"

    zip_file_path = os.path.join(zip_file_directory, "train.zip.001")

    if os.path.exists(zip_file_path):
        extract_zip_files(zip_file_path, input_directory)
    else:
        print(f"File not found: {zip_file_path}")
        exit(1)

    # create output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    resize_and_crop_image(input_directory, output_directory)
    print("Image resizing and cropping complete.")
