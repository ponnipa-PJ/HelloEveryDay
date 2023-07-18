from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from pythainlp.corpus.common import thai_words
from pythainlp import Tokenizer,word_tokenize
import numpy as np
import cv2
import imutils  # https://pypi.org/project/imutils/

import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def hello():
    return "Welcome To WebService"

@app.route('/findedge')
def findedged():
    # path = id+'.jpg'
    path = '1.jpg'
    img = cv2.imread(path)
    print(img.shape) # Print image shape
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]
    # print(s)
    # Apply threshold on s - use automatic threshold algorithm (use THRESH_OTSU).
    ret, thresh = cv2.threshold(s, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Find contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts) 
    # print(cnts)
    # Find the contour with the maximum area.
    c = max(cnts, key=cv2.contourArea)

    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(c)
    # print(c)
    # Crop the bounding rectangle out of img
    out = img[y:y+h, x:x+w, :].copy()
    # Show result (for testing).
    # print(x, y, w, h)


    # x, y, w, h = 30, 381, 900, 899
    # out = img[y:y+h, x:x+w, :].copy()
    # cv2.imshow('out', out)
        
    # Save the cropped image
    cv2.imwrite("out1.jpg", out)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return str(x)+" " +str(y)+" " +str(w)+" " +str(h)

@app.route('/worktoken')
def get_predictmotor():
    # print(request.args.get)
    text = request.args.get('text')
    words = set(thai_words())  # thai_words() returns frozenset
    words.add("ข้อมูลจำเพาะ") 
    words.add("หมายเลขใบอนุญาต/อย.")
    custom_tokenizer = Tokenizer(words)
    result = custom_tokenizer.word_tokenize(text)
    result = " ".join(result)
    result = result.replace('  ', '')
    result = result.replace(' ', '<span style="color:red"> | </span>')
    return result

@app.route('/scraping')
def scraping():
    id = request.args.get('id')
    path = request.args.get('path')
    path = path.replace("'",'')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=960,720')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('file:///Users/ponnipa/Documents/GitHub/fda-backend/'+path)
    sleep(1)
# (1382, 2400, 3)
    driver.get_screenshot_as_file(id+".jpg")
    driver.quit()
    print("end...")
    path = id+'.jpg'
    img = cv2.imread(path)
    print(img.shape) # Print image shape
    # cv2.imshow("original", img)
    
    x, y, w, h = 30, 381, 900, 899
    out = img[y:y+h, x:x+w, :].copy()

    # Display cropped image
    # cv2.imshow("cropped", cropped_image)
    
    # Save the cropped image
    cv2.imwrite("Cropped"+id+".jpg", out)
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return "success"

@app.route('/base64')
def get_base64():
    id = request.args.get('id')
    print(id)
    with open("Cropped"+id+".jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    # print(encoded_string)
    return encoded_string

if __name__ == "__main__":
    app.run(debug=False)