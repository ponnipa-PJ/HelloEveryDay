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
pathbackend = requests.get('http://localhost:8081/api/database_path')
# url = data.backend_path
backend_path = json.loads(pathbackend.text)
backend_path = backend_path["backend_path"]

@app.route('/')
def hello():
    return "Welcome To WebService"

@app.route('/findedge')
def findedged():
    # path = id+'.jpg'
    path = '10.jpg'
    img = cv2.imread(path)
    # print(img.shape) # Print image shape
    
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
    # print(namereal_result)
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    cat = requests.get('http://localhost:8081/api/fdatypes')
    cats = cat.text
    cats = json.loads(cats)
    my_array_cat = np.asarray(cats)
    for arr in my_array_cat:
        # print (restaurant['name'])
        arra = arr['name']
        words.add(arra) 
    
    keyword_dicts = requests.get('http://localhost:8081/api/keyword_dicts?status=1')
    keyword_dicts = keyword_dicts.text
    keyword_dicts = json.loads(keyword_dicts)
    keyword_dicts = np.asarray(keyword_dicts)
    key = ''
    
    for restaurant in keyword_dicts:
        # print (restaurant['name'])
        value = restaurant['name']
        key += restaurant['name']
        words.add(value) 
        
    # print(key)
    namereal_result = namereal_result + key
    custom_tokenizer = Tokenizer(words)
    name_word = custom_tokenizer.word_tokenize(text)
    namereal_result = custom_tokenizer.word_tokenize(namereal_result)
    # print(text)
    for arr in my_array_cat:
        # print (restaurant['name'])
        arra = arr['name']
        namereal_result.append(arra) 
    # result = " ".join(result)
    
    # result = result.replace('  ', '')
    # result = result.replace(' ', ' | ')
    
    # result = result.replace(' ', '<span style="color:red"> | </span>')
    name_match = []
    name_list = ''
    # print(namereal_result)
    # print(text)
    # print(name_word)
    for te in name_word:
        if te != ' ':
            if any(word.startswith(te) for word in namereal_result):
                # print(name_word)
                name_match.append(te)
    # print('name_match',name_match)
    # print('name_word',name_word)
    for item in name_word:
        # print(item)
        if item != ' ' and item != '(' and item != ')':
            # print(item)
            if any(word.startswith(item) for word in name_match):
                # cut = custom_tokenizer.word_tokenize(item)
                # for c in cut:
                if item in namereal_result:
                    # print(item)
                    na = ' | <span style="color:red">'+item+'</span>' 
                else:
                    na = ' | ' + item
                    
                # print(na)
            else:
                na = ' | ' + item
                # print('item',na)
        else:
            na = ''
        name_list += na
    
    # name_list = name_list.replace(" | | '",'')
    # print(name_list)
    # print(category)
    # print(json.dumps(value, ensure_ascii=False).encode('utf8'))
    Str = name_list.split('|', 1)[-1]
    # Str = Str[:-1]
    # print(Str)
    return str(Str)

@app.route('/tokenkeyword')
def tokenkeyword():
    text = request.args.get('text')
    
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
    name_word = custom_tokenizer.word_tokenize(text)
    # name_word = word_tokenize(text, engine="longest")
    
    
    return str(name_word)


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
    for name_word in namereal_result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in name_result):
                # print(name_word)
                name_match.append(name_word)
    # print(name_result)
    # print(name_match)
    listfull = []
    for item in name_result:
        na = ''
        if item != ' ' and item != '(' and item != ')' and item != 'ผล':
            if any(word.startswith(item) for word in name_match):
                # print('list',listfull)
                if item not in listfull and len(item) > 1:
                    # print(item)
                    listfull.append(item)
                    na = '<span style="color:red">'+item+'</span>&nbsp; '
                    # na = item
        name_list += na
        
    
    # print(listfull)
    res = [*set(listfull)]
    listToStr = ' '.join([str(elem) for elem in res])
    listToStr.replace('ผล','')
    return str(name_list)

# @app.route('/checkkeyword')
# def checkkeyword():
#     name = request.args.get('name')
#     name_real = request.args.get('name_real')
#     # name_real = 'ช่วยลดความอยากอาหาร'
#     x = requests.get('http://localhost:8081/api/dicts?status=1')
#     dicts = x.text
#     dicts = json.loads(dicts)
#     words = set(thai_words())  # thai_words() returns frozenset
#     my_array = np.asarray(dicts)
    
#     for restaurant in my_array:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         words.add(value) 
    
#     keyword_dicts = requests.get('http://localhost:8081/api/keyword_dicts?status=1')
#     keyword_dicts = keyword_dicts.text
#     keyword_dicts = json.loads(keyword_dicts)
#     keyword_dicts = np.asarray(keyword_dicts)
    
#     for restaurant in keyword_dicts:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         words.add(value) 
        
#     custom_tokenizer = Tokenizer(words)
#     name_result = custom_tokenizer.word_tokenize(name)
#     namereal_result = custom_tokenizer.word_tokenize(name_real)
#     # print(name_result)
#     # print('namereal_result',namereal_result)
    
#     name_match = []
#     name_list = ''
#     sentence = ''
#     for name_word in namereal_result:
#         if name_word != ' ':
#             if any(word.startswith(name_word) for word in name_result):
#                 # print(name_word)
#                 name_match.append(name_word)
#     # print(name_result)
#     # print(name_match)
#     listfull = []
#     for item in name_result:
#         na = ''
#         if item != ' ' and item != '(' and item != ')' and item != 'ผล':
#             if any(word.startswith(item) for word in name_match):
#                 print('list',item)
#                 if item not in listfull:
#                     print(item)
#                     listfull.append(item)
#                     na = item
#                     # na = item
#         name_list += na
    
#     name_list = name_real
#     # print(name_list)
#     # print(listfull)
#     # print(name.index(name_list))
#     front = name[:name.index(name_list)]
#     # print('front',front)
#     frontsplit = front.split(" ")
#     # print(frontsplit)
#     # print(len(frontsplit))
#     for f in frontsplit:
#         last_item = frontsplit[-1]
#         if last_item == '':
#             frontsplit = frontsplit[:-1] 
         
#     frontsentence = (frontsplit[-1])
#     # print(frontsplit)
#     back = name[name.index(name_list):]
#     backsplit = back.split(" ")
#     # print(len(backsplit))
#     if len(backsplit) == 2:
#         backsentence = backsplit[1]
#     else:
#         backsentence = backsplit[1]+ " " +backsplit[2]
    
#     sentence = frontsentence + " " + '<span style="color:red">'+name_list+'</span>'+ " " +backsentence
#     return str(sentence)

@app.route('/checkkeyword')
def checkkeyword():
    name = request.args.get('name')
    # name_real = 'ช่วยลดความอยากอาหาร'
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    
    keyword_dicts = requests.get('http://localhost:8081/api/keyword_dicts?status=1')
    keyword_dicts = keyword_dicts.text
    keyword_dicts = json.loads(keyword_dicts)
    keyword_dicts = np.asarray(keyword_dicts)
    
    k = ''
    for restaurant in keyword_dicts:
        # print (restaurant['name'])
        value = restaurant['name']
        k+=restaurant['name']
        words.add(value) 
        
    # print('k',k)
    custom_tokenizer = Tokenizer(words)
    name_result = custom_tokenizer.word_tokenize(name)
    namereal_result = custom_tokenizer.word_tokenize(k)
    # print(name_result)
    # print('namereal_result',namereal_result)
    
    name_match = []
    name_list = ''
    sentence = ''
    for name_word in namereal_result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in name_result):
                # print(name_word)
                name_match.append(name_word)
    # print('name_result',name_result)
    # print('name_match',name_match)
    listfull = []
    for item in name_result:
        na = ''
        if item != ' ' and item != '(' and item != ')' and item != 'ผล':
            # print(item)
            if any(word.startswith(item) for word in namereal_result):
                # print('list',item)
                if item not in listfull:
                    # print(item)
                    listfull.append(item)
                    na = item
                    # na = item
        name_list += na
    
    # name_list = name_real
    # print(listfull)
    for l in listfull:
        
        # print(listfull)
        # print(name.index(name_list))
        front = name[:name.index(l)]
        # print('front',front)
        frontsplit = front.split(" ")
        # print('frontsplit',frontsplit)
        # print(len(frontsplit))
        for f in frontsplit:
            last_item = frontsplit[-1]
            if last_item == '':
                frontsplit = frontsplit[:-1] 
            
        frontsentence = (frontsplit[-1])
        # print(frontsplit)
        back = name[name.index(l):]
        backsplit = back.split(" ")
        # print('backsplit',backsplit)
        if len(backsplit) == 2:
            backsentence = backsplit[1]
        else:
            backsentence = backsplit[1]+ " " +backsplit[2]
        
        sentence += frontsentence + " " + '<span style="color:red">'+backsplit[0]+'</span>'+ " " +backsentence+'</br>'
        # print(sentence)
    return str(sentence)


def Repeat(x):
    _size = len(x)
    repeated = ''
    for i in range(_size):
        k = i + 1
        for j in range(k, _size):
            if x[i] == x[j] and x[i] not in repeated:
                repeated += '<span style="color:red">'+x[i]+'</span>&nbsp;'
    return repeated

@app.route('/matchcategory')
def matchcategory():
    category = request.args.get('category')
    
    x = requests.get('http://localhost:8081/api/dicts?status=1')
    dicts = x.text
    dicts = json.loads(dicts)
    words = set(thai_words())  # thai_words() returns frozenset
    my_array = np.asarray(dicts)
    
    cat = requests.get('http://localhost:8081/api/fdatypes')
    cats = cat.text
    cats = json.loads(cats)
    my_array_cat = np.asarray(cats)
    # print(my_array_cat)
    cats_arr = []
    for restaurant in my_array_cat:
        # print (restaurant['name'])
        value = restaurant['name']
        cats_arr.append(value)
    # print(cats_arr)
        
    for restaurant in my_array:
        # print (restaurant['name'])
        value = restaurant['name']
        words.add(value) 
    # print(words)
    custom_tokenizer = Tokenizer(words)
    name_result = custom_tokenizer.word_tokenize(category)
    # print(name_result)
    # print(type(name_result))
    namereal_result = cats_arr
    name_match = []
    name_list = ''
    # print(name_result)
    for name_word in namereal_result:
        if name_word != ' ':
            if any(word.startswith(name_word) for word in name_result):
                # print(name_word)
                name_match.append(name_word)
    # print(name_match)
    # print(name_result)
    for item in name_result:
        na = ''
        if item != ' ' and item != '(' and item != ')':
            if any(word.startswith(item) for word in name_match) and len(item) > 1:
                    na = '<span style="color:red">'+item+'</span>' 
                    # na =item
                    name_list = na
                    break

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
    options = webdriver.ChromeOptions()
    service = Service()
    options.add_argument('--headless')
    options.add_argument('--window-size=960,720')
    driver = webdriver.Chrome(service=service, options=options)
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--window-size=960,720')
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(backend_path+path)
    sleep(1)
# (1382, 2400, 3)
    driver.get_screenshot_as_file(id+".jpg")
    driver.quit()
    # print("end...")
    path = id+'.jpg'
    img = cv2.imread(path)
    # print(img.shape) # Print image shape
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
    # print(backend_path)
    path = request.args.get('path')
    path = path.replace("'",'')
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--window-size=960,720')
    options = webdriver.ChromeOptions()
    service = Service()
    options.add_argument('--headless')
    options.add_argument('--window-size=960,720')
    driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(backend_path+path)
    # print(backend_path+path)
    # print(driver.page_source) 
    inputElement = driver.find_element(By.CLASS_NAME,"product-detail")
    the_text = inputElement.text
    # print(the_text)
    return the_text

@app.route('/scrapingheader')
def scrapingheader():
    # print(backend_path)
    path = request.args.get('path')
    path = path.replace("'",'')
    options = webdriver.ChromeOptions()
    service = Service()
    options.add_argument('--headless')
    options.add_argument('--window-size=960,720')
    driver = webdriver.Chrome(service=service, options=options)
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--window-size=960,720')
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(backend_path+path)
    # print(driver.page_source) 
    inputElement = driver.find_element(By.CLASS_NAME,"_44qnta")
    the_text = inputElement.text
    # print(the_text)
    return the_text

@app.route('/base64')
def get_base64():
    id = request.args.get('id')
    # print(id)
    with open("Cropped"+id+".jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    # print(encoded_string)
    return encoded_string

if __name__ == "__main__":
    app.run(debug=False)