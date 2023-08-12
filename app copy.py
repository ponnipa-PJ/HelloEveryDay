from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from pythainlp.corpus.common import thai_words
from pythainlp import Tokenizer,word_tokenize
import numpy as np
import cv2
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
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=691,1200')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('file:///Users/ponnipa/Documents/GitHub/shophtml/2.html')
    sleep(1)

    driver.get_screenshot_as_file("2.jpg")
    driver.quit()
    # print("end...")
    path = '2.jpg'
    img = cv2.imread(path)
    # print(img.shape) # Print image shape
    # cv2.imshow("original", img)
    # Cropping an image
    # top bottom left right
    # cropped_image = img[180:650, 300:850]
    cropped_image = img[380:1280, 30:930]

    # Display cropped image
    # cv2.imshow("cropped", cropped_image)
    
    # Save the cropped image
    cv2.imwrite("Cropped2.jpg", cropped_image)
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return "success"

@app.route('/base64')
def get_base64():
    with open("Cropped Image2.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    # print(encoded_string)
    return encoded_string

if __name__ == "__main__":
    app.run(debug=False)