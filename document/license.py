from pytesseract import image_to_string
import cv2
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import base64

options = webdriver.FirefoxOptions()
options.binary_location = r"/usr/lib/firefox/firefox-bin"
driver = webdriver.Firefox(options=options)
driver.get('https://parivahan.gov.in/rcdlstatus/?pur_cd=101')

def get_captcha():
    captcha = driver.find_element(By.ID,'form_rcdl:j_idt45:j_idt53')
    captcha.screenshot('captcha.png')
    #encrypt with base64
    with open("captcha.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return "data:application/image;base64," +encoded_string.decode('utf-8')

def check_validity(captcha, user_data):
    #Enters the needed data into the website and submits it
    dlno_form = driver.find_element(By.CSS_SELECTOR, "#form_rcdl\:tf_dlNO")
    dob_form = driver.find_element(By.CSS_SELECTOR, "#form_rcdl\:tf_dob_input")
    captcha_form = driver.find_element(By.CSS_SELECTOR,  "#form_rcdl\:j_idt45\:CaptchaID")
    dlno_form.send_keys(user_data["dln"])
    dob_form.send_keys(user_data["dob"])
    captcha_form.send_keys(captcha)
    submit_button = driver.find_element(By.CSS_SELECTOR, "#form_rcdl\:j_idt60")
    submit_button.click()
    #Wait for the result to be displayed
    sleep(.5)
    #Check if we failed the captcha and return status
    captcha_failed=driver.find_elements(By.CSS_SELECTOR, "#form_rcdl\:j_idt19")
    sleep(5)
    status = driver.find_elements(By.CSS_SELECTOR,"#form_rcdl\:j_idt91 > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(2) > span")
    if captcha_failed and not status:
        return {"status":"captcha_failed"}
    #Check if the result is valid
    holder_name = driver.find_element(By.CSS_SELECTOR,"table.table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2)").get_attribute("innerHTML")
    till_date = driver.find_element(By.CSS_SELECTOR, "#form_rcdl\:j_idt91 > table:nth-child(8) > tbody > tr:nth-child(1) > td:nth-child(3) > span").get_attribute("innerHTML")
    if status[0].get_attribute("innerHTML") == "ACTIVE":
        return {"status":True, "name":holder_name, "till_date":till_date}
    else:
        return {"status":False}



def extract_text(image_path):
    dob = None
    name = None
    dlnp = None
    img = cv2.imread(image_path)
    variant_one = img;
    # Now we process the image based on two values first we run basic image manipulation
    # and then we run OCR on the image.If we don't detect anything then we apply canny and 
    # extract the text from the image
    variant_one = cv2.cvtColor(variant_one, cv2.COLOR_BGR2GRAY)
    variant_one = cv2.resize(variant_one, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    otsu = cv2.threshold(variant_one, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    ocr_attempt_one = image_to_string(variant_one)
    #Extract the driver license number
    dl_num_patn = r'\b[A-Z]{2}[0-9]{2}[ |A-Z][0-9]{11}'
    match = re.search(dl_num_patn, ocr_attempt_one)
    if match:
        dlnp = match.group()
    #Get the date of birth
    dob_match_pattern = r'[0-9]{2}'+"-"+r'[0-9]{2}'+"-"+r'[0-9]{4}'
    match = re.search(dob_match_pattern, ocr_attempt_one)
    if match:
        dob = match.group()
    index = match.end()
    for char in ocr_attempt_one[index:]:
        if char == '\n':
            break
        index+=1
    last_index = index
    for char in ocr_attempt_one[index+1:]:
        if char == '\n':
            break
        last_index+=1
    name = ocr_attempt_one[index:last_index+1].strip()
    return{"dln":dlnp, "dob":dob, "name":name}

if __name__ == "__main__":
    data = extract_text('/home/guhan-sensam/Pictures/dlv.jpg')
    print(data)
    print(get_captcha())
    captcha = input("Enter Captcha:")
    print(check_validity(captcha, data))
