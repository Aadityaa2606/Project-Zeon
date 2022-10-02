# Query Indian Government website and check if aadhar card is verified
from pytesseract import image_to_string
import cv2
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

options = webdriver.FirefoxOptions()
options.binary_location = r"/usr/lib/firefox/firefox-bin"
driver = webdriver.Firefox(options=options)
driver.get('https://myaadhaar.uidai.gov.in/verifyAadhaar')


def get_captcha():
    # Gets the captcha string and returns it as base64 encoded string that aadhi can display
    img = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[2]/img')
    return img.get_attribute("src")

def check_aadhar(user_data):
    #Checks if the aadhar number is valid
    anumfield = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[3]/div/div/div[1]/div/form/div/div[1]/div/div/div/input')
    anumfield.send_keys(user_data['aadhar_num'])
    sleep(2)
    notFound = driver.find_elements(By.XPATH,'/html/body/div[1]/div/div[3]/div/div/div[1]/div/form/div/div[1]/div/div[2]/span')
    if notFound:
        return 0
    else:
        return 1


def check_validity(captcha, user_data):
    captchafield = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[3]/div/div/div[1]/div/form/div/div[2]/div[1]/div/div/div/input')
    button = driver.find_element(By.CLASS_NAME,'button_btn__1dRFj')
    #Now we can check here if the aadhar number is blocked
    captchafield.send_keys(captcha)
    button.click()
    sleep(3)
    button.click()
    sleep(1.5)
    toast = driver.find_elements(By.CSS_SELECTOR,"#verifyAadhaarAPI")
    if toast:
        return {"status":0,"message":"Invalid Captcha"}
    # we wait for the verified page to appear
    myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'verify-aadhaar-response__cong')))
    #Now we get the verified status
    verified = driver.find_element(By.CLASS_NAME,'verify-aadhaar-response__cong')
    if "Exists" in verified.get_attribute("innerHTML"):
        return {"status":"verified"}
    else:
        return {"status":0,"message":"Blocked Aadhar Number"}

def extract_text(image_path):
    dob = None
    name = None
    gender = None
    a_num = None
    img = cv2.imread(image_path)
    variant_one = img;
    # Now we process the image based on two values first we run basic image manipulation
    # and then we run OCR on the image.If we don't detect anything then we apply canny and 
    # extract the text from the image
    variant_one = cv2.cvtColor(variant_one, cv2.COLOR_BGR2GRAY)
    variant_one = cv2.resize(variant_one, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    otsu = cv2.threshold(variant_one, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    ocr_attempt_one = image_to_string(variant_one)
    # Extract the full name of the person
    adhar_name_patn = r'\b[A-Z][a-z]*'+r" "+r'[A-Z][a-z]*\b'
    split_ocr = ocr_attempt_one.split('\n')
    for ele in split_ocr:
        match = re.search(adhar_name_patn, ele)
        if match:
            name = match.group()
            break
    # Get the Dob
    if 'DOB' in ocr_attempt_one:
        index = ocr_attempt_one.find("DOB")
        # read only numbers till new line character
        dob = ""
        for char in (ocr_attempt_one[index:]):
            if char == '\n':
                break
            dob += char
        #now process the dob
        date = ''
        month = ''
        year = ''
        try:
            dob = dob.split(':')[1].strip()
        except:
            dob = dob.split('DOB')[1].strip()
        date = dob[:2]
        for char in dob[2:-5]:
            if char in ['1','2','3','4','5','6','7','8','9']:
                month += char
                month = dob[dob.index(char)-1] + char
        year = dob[::-1][:4][::-1]
        dob = date + '/' + month + '/' + year
    # get the gender
    if re.search('[Mm][Aa][Ll][Ee]', ocr_attempt_one):
        gender = "male"
    elif re.search('[Ff][Ee][Mm][Aa][Ll][Ee]',ocr_attempt_one):
        gender = "female"
    else:
        gender = None
    #Attempt to get the aadhar number
    anumPattern = '[0-9]{4}\s[0-9]{4}\s[0-9]{4}'
    num_found = False
    match = re.search(anumPattern, ocr_attempt_one)
    if match:
        a_num = match.group()
        num_found = True
    if not num_found:
        variant_two = cv2.imread(image_path)
        canny = cv2.Canny(variant_two, 50, 100)
        ocr_attempt_two = image_to_string(canny)
        match = re.search(anumPattern, ocr_attempt_two)
        if match:
            a_num = match.group()
    return {"name":name, "gender":gender, "dob":dob, "aadhar_num":a_num}

data = extract_text('/home/guhan-sensam/Desktop/Hackoverflow/zeon-backend-test/test2.jpg')

if __name__ == "__main__":
    if check_aadhar(data):
        captcha = get_captcha()
        print(captcha)
        sh = input("Enter the Captcha:")
        print(check_validity(sh, data))
    else:
        print("rejected")



    
        
