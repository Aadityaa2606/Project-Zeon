from pytesseract import image_to_string
import cv2
import re


def extract_text(image_path):
    img = cv2.imread(image_path)
    variant_one = img;
    # Now we process the image based on two values first we run basic image manipulation
    # and then we run OCR on the image.If we don't detect anything then we apply canny and 
    # extract the text from the image
    variant_one = cv2.cvtColor(variant_one, cv2.COLOR_BGR2GRAY)
    variant_one = cv2.resize(variant_one, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    otsu = cv2.threshold(variant_one, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    ocr_attempt_one = image_to_string(variant_one)
    # Attempt to extract the name of the person
    print(ocr_attempt_one)
    name = None
    lines = ocr_attempt_one.split('\n')
    for a in range(len(lines)):
        if lines[a].find("Given Name") != -1:
            name = lines[a+1].strip()
            break



extract_text("/home/guhan-sensam/Desktop/Hackoverflow/zeon-backend-test/passport2.jpg")