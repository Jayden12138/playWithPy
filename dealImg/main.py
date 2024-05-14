import os
import glob
from image_utils import extract_data_from_image
from excel_utils import fill_excel_with_data

def process_images_in_folder(folder_path):
    print(f"Processing images in folder: {folder_path}")
    image_files = glob.glob(os.path.join(folder_path, '*.jpg'))
    print(f"Found image files: {image_files}")

    for image_file in image_files:
        extracted_data = extract_data_from_image(image_file)

        if all(extracted_data):
            excel_path = 'target.xlsx'
            fill_excel_with_data(excel_path, extracted_data)
        else:
            print(f"Failed to extract valid data from {image_file}")

if __name__ == "__main__":
    image_folder = 'image_folder'
    process_images_in_folder(image_folder)
