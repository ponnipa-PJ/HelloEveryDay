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
import requests
import json
# from ocrmac import ocrmac
    
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# annotations = ocrmac.OCR('Cropped2.jpg').recognize()
# print(annotations)
# ocrmac.OCR('Cropped3.jpg').annotate_PIL()
  
@app.route('/')
def hello():
    return "Welcome To WebService"

@app.route('/findedge')
def findedged():
    # path = id+'.jpg'
    path = '2.jpg'
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
    cv2.imwrite("out.jpg", out)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return str(x)+" " +str(y)+" " +str(w)+" " +str(h)

@app.route('/worktoken')
def worktoken():
    text = request.args.get('text')
    namereal_result = request.args.get('namereal_result')
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    # print(words)
    custom_tokenizer = Tokenizer(words)
    result = custom_tokenizer.word_tokenize(text)
    namereal_result = custom_tokenizer.word_tokenize(namereal_result)
    # result = " ".join(result)
    
    # result = result.replace('  ', '')
    # result = result.replace(' ', ' | ')
    
    # result = result.replace(' ', '<span style="color:red"> | </span>')
    name_match = []
    name_list = ''
    print(name_match)
    for name_word in result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in namereal_result):
                print(name_word)
                name_match.append(name_word)
    print(name_match)
    for item in result:
        na = item
        if item != ' ' and item != '(' and item != ')':
            if any(word.startswith(item) for word in name_match):
                    na = ' | <span style="color:red">'+item+'</span>' 
        name_list += na
    # print(name_list)
    # print(category)
    # print(json.dumps(value, ensure_ascii=False).encode('utf8'))
    return str(name_list)

@app.route('/matchname')
def matchname():
    category = [request.args.get('category')]
    name = request.args.get('name')
    name_real = request.args.get('name_real')
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    # print(words)
    custom_tokenizer = Tokenizer(words)
    name_result = custom_tokenizer.word_tokenize(name)
    # print(name_result)
    # print(type(name_result))
    namereal_result = custom_tokenizer.word_tokenize(name_real)
    name_match = []
    name_list = ''
    for name_word in name_result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in namereal_result):
                print(name_word)
                name_match.append(name_word)
    
    for item in name_result:
        na = item
        if item != ' ' and item != '(' and item != ')':
            if any(word.startswith(item) for word in name_match):
                    na = '<span style="color:red">'+item+'</span>' 
        name_list += na
    # print(name_list)
    # print(category)
    value = {
        "category": category,
        "name": name_list,
    }
    # print(json.dumps(value, ensure_ascii=False).encode('utf8'))
    return str(name_list)

@app.route('/matchcategory')
def matchcategory():
    category = request.args.get('category')
    category_real = request.args.get('category_real')
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    # print(words)
    custom_tokenizer = Tokenizer(words)
    name_result = custom_tokenizer.word_tokenize(category)
    # print(name_result)
    # print(type(name_result))
    namereal_result = custom_tokenizer.word_tokenize(category_real)
    name_match = []
    name_list = ''
    # print(name_result)
    # print(namereal_result)
    for name_word in namereal_result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in name_result):
                # print(name_word)
                name_match.append(name_word)
    print(name_match)
    print(name_result)
    for item in name_result:
        na = ''
        if item != ' ' and item != '(' and item != ')':
            if any(word.startswith(item) for word in name_match):
                    na = '<span style="color:red">'+item+'</span>' 
                    # na =item
        name_list += na

    # print(json.dumps(value, ensure_ascii=False).encode('utf8'))
    return str(name_list)


# @app.route('/matchcategory')
# def matchcategory():
#     category = request.args.get('category')
#     category_real = request.args.get('category_real')
#     x = requests.get('http://localhost:8081/api/dicts?status=1')
#     dicts = x.text
#     dicts = json.loads(dicts)
#     words = set(thai_words())  # thai_words() returns frozenset
#     # print(words)
#     my_array = np.asarray(dicts)
#     for restaurant in my_array:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         words.add(value) 
#     # print(words)
#     custom_tokenizer = Tokenizer(words)
#     category_real = custom_tokenizer.word_tokenize(category_real)
#     category = custom_tokenizer.word_tokenize(category)
#     name_match = []
#     name_list = ''
#     # print(category)
#     # print(category_real)
#     for name_word in category:
#         if name_word != ' ':
#             if any(word.startswith(name_word) for word in category_real):
#                 # print(name_word)
#                 name_match.append(name_word)
    
#     for item in category:
#         na = item
#         if item != ' ' and item != '(' and item != ')':
#             if any(word.startswith(item) for word in name_match):
#                     na = '<span style="color:red">'+item+'</span>' 
#         name_list += na + ' '
#     # print(name_list)
                
#     return str(name_list)


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

@app.route('/scrapingcontent')
def scrapingcontent():
    path = request.args.get('path')
    path = path.replace("'",'')
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=960,720')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('file:///Users/ponnipa/Documents/GitHub/fda-backend/'+path)
    # print(driver.page_source) 
    inputElement = driver.find_element(By.CLASS_NAME,"product-detail")
    the_text = inputElement.text
    # print(the_text)
    return the_text


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