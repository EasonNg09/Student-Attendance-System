import cv2
import pytesseract
import sys
import os

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

def perform_ocr():
    print(f'-----------')
    
    file_path = os.environ.get('FILE_PATH')
    print(f"Attempting to read image from: {file_path}")
    image = cv2.imread(file_path)

    if image is None:
        print(f"Error: Unable to load image from {file_path}")

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

    denoised_image = cv2.fastNlMeansDenoising(binary_image, None, 10, 7, 21)

    custom_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(denoised_image, config=custom_config, lang='eng')

    #print("Extracted Text from Image:")
    print(extracted_text)

if __name__ == "__main__":
    perform_ocr()

# # Load the image using OpenCV
# image_path = r'C:\FYP Code\Uploads\Simage.jpg'
# image = cv2.imread(image_path)
# #image = cv2.imread('C:\FYP Code/algorithm\Verification\image.jpg')
# #image = cv2.imread('C:\FYP Code/uploads\image.jpg')
# # image = cv2.imread(file_path)

# # Preprocessing steps to enhance OCR accuracy
# # 1. Convert the image to grayscale
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # 2. Apply thresholding to binarize the image
# _, binary_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)

# # 3. Apply noise reduction techniques, such as denoising
# denoised_image = cv2.fastNlMeansDenoising(binary_image, None, 10, 7, 21)

# # 4. Perform OCR on the preprocessed image with custom configurations
# custom_config = r'--oem 3 --psm 6'
# extracted_text = pytesseract.image_to_string(denoised_image, config=custom_config, lang='eng')

# # Print the extracted text
# print("Extracted Text from Image:")
# print(extracted_text)