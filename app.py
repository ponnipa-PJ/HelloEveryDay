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
    text = text.replace(' ', '')
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
    
    # keyword_dicts = requests.get('http://localhost:8081/api/keyword_dicts?status=1')
    # keyword_dicts = keyword_dicts.text
    # keyword_dicts = json.loads(keyword_dicts)
    # keyword_dicts = np.asarray(keyword_dicts)
    # key = ''
    
    # for restaurant in keyword_dicts:
    #     # print (restaurant['name'])
    #     value = restaurant['name']
    #     key += restaurant['name']
    #     words.add(value) 
        
    # print(key)
    namereal_result = namereal_result 
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

# @app.route('/worktokendesc')
# def worktokendesc():
#     text = request.args.get('text')
#     namereal_result = request.args.get('namereal_result')
#     # print(namereal_result)
#     x = requests.get('http://localhost:8081/api/dicts?status=1')
#     dicts = x.text
#     dicts = json.loads(dicts)
#     words = set(thai_words())  # thai_words() returns frozenset
#     my_array = np.asarray(dicts)
#     for restaurant in my_array:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         words.add(value) 
#     cat = requests.get('http://localhost:8081/api/fdatypes')
#     cats = cat.text
#     cats = json.loads(cats)
#     my_array_cat = np.asarray(cats)
#     for arr in my_array_cat:
#         # print (restaurant['name'])
#         arra = arr['name']
#         words.add(arra) 
    
#     keyword_dicts = requests.get('http://localhost:8081/api/keyword_dicts?status=1')
#     keyword_dicts = keyword_dicts.text
#     keyword_dicts = json.loads(keyword_dicts)
#     keyword_dicts = np.asarray(keyword_dicts)
#     key = []
    
#     for restaurant in keyword_dicts:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         key.append(restaurant['name'])
#         words.add(value) 
        
    
#     custom_tokenizer = Tokenizer(words)
#     name_word = custom_tokenizer.word_tokenize(text)
#     # namereal_result = custom_tokenizer.word_tokenize(key)
#     namereal_result = key
#     # print(namereal_result)
#     # print(key)
#     # print(name_word)
#     name_match = []
#     name_list = ''
#     # print(namereal_result)
#     # print(text)
#     # print(name_word)
#     for te in name_word:
#         if te != ' ':
#             if any(word.startswith(te) for word in namereal_result):
#                 # print(name_word)
#                 name_match.append(te)
                
#     print('name_match',name_match)
#     # print('name_word',name_word)
#     for item in name_word:
#         # print(item)
#         if item != ' ' and item != '(' and item != ')':
#             # print(item)
#             if any(word.startswith(item) for word in name_match) and len(item) != 1:
#                 # cut = custom_tokenizer.word_tokenize(item)
#                 # for c in cut:
#                 if item in name_match:
#                     # print(item)
#                     na = '<span style="color:red">'+item+'</span>' 
#                 else:
#                     na = item
                    
                    
#                 # print(na)
#             else:
                
#                 na = item
#                 # print('item',na)
#         else:
#             na = ' '
#         name_list += na
    
#     # name_list = name_list.replace(" | | '",'')
#     # print(name_list)
#     # print(category)
#     # print(json.dumps(value, ensure_ascii=False).encode('utf8'))
#     Str = name_list.split('|', 1)[-1]
#     # Str = Str[:-1]
#     # print(Str)
#     return str(Str)

@app.route('/worktokendesc')
def worktokendesc():
    name = request.args.get('text')
    # name = name.replace(' ', '')
    # name = 'หรือหลังอาหารมื้อแรก ถ้ายังรู้สึกหิวปรับทาน 2 แคปซูล หลังอาหารมื้อแรกของวัน'
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
    key = []
    for restaurant in keyword_dicts:
        # print (restaurant['name'])
        value = restaurant['name']
        k+=restaurant['name']
        key.append(restaurant['name'])
        words.add(value) 
    # print('k',k)
    custom_tokenizer = Tokenizer(words)
    name_result = custom_tokenizer.word_tokenize(name)
    # namereal_result = custom_tokenizer.word_tokenize(k)
    # print('name_result',name_result)
    namereal_result = key
    # print('namereal_result',namereal_result)
    listfull=[]
    for item in name_result:
        na = ''
        if item != ' ' and item != '(' and item != ')' and item != 'ผล':
            # print(item)
            # if any(word.startswith(item) for word in namereal_result):
            for real in namereal_result:
                if item in real:
                    listfull.append(item)
                    
                    
    # print('listfull',listfull)
    
    for k in key:
        t = name.replace(k,'<span style="color:red">'+k+'</span>')
        name = t

    # print(t)
    # print('name',name)
    return name


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

# @app.route('/checkkeyword')
# def checkkeyword():
#     name = request.args.get('name')
#     # name = name.replace(' ', '')
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
    
#     k = ''
#     for restaurant in keyword_dicts:
#         # print (restaurant['name'])
#         value = restaurant['name']
#         k+=restaurant['name']
#         words.add(value) 
#     # print('k',k)
#     custom_tokenizer = Tokenizer(words)
#     name_result = custom_tokenizer.word_tokenize(name)
#     namereal_result = custom_tokenizer.word_tokenize(k)
#     # print('name_result',name_result)
#     # print('namereal_result',namereal_result)
    
#     name_match = []
#     name_list = ''
#     sentence = []
#     for name_word in namereal_result:
#         if name_word != ' ':
#             if any(word.startswith(name_word) for word in name_result):
#                 # print(name_word)
#                 name_match.append(name_word)
#     # print('name_result',name_result)
#     # print('name_match',name_match)
#     # print('name_match',name_match)
#     listfull = []
#     frontsentence =[]
#     for item in name_result:
#         na = ''
#         if item != ' ' and item != '(' and item != ')' and item != 'ผล':
#             # print(item)
#             # if any(word.startswith(item) for word in namereal_result):
#             if item in namereal_result:
                
#                 # print('list',item)
#                 if item not in listfull:
#                     # print(item)
#                     listfull.append(item)
#                     na = item
#                     # na = item
#         name_list += na
    
#     # name_list = name_real
#     name = 'รายละเอียดสินค้าแท้% Fercy Fiber S เฟอร์ซี่ ไฟเบอร์ เอส Fercy Diet เฟอซี่ไดเอทFercy Diet เฟอร์ซี่ เคล็ดลับหุ่นดี คุมหิว อิ่มนาน น้ำหนักลงง่ายๆ ไม่ต้องอด ช่วยลดความอยากอาหาร ดักจับไขมัน ช่วยกระตุ้นการเผาผลาญและการขับถ่าย กำจัดไขมันส่วนเกิน ช่วยดูแลรูปร่างให้กระชับ'
#     # print('name',name)
#     # print(listfull)
#     for n in range(len(name)):
#         # print(n)
#         for l in listfull:
#             for ll in l:
#                 # print(ll,'ll')
#                 # print(name[n],'n')
#                 if name[n] == ll:
#                     # print(name[n:n+len(l)])
#                     if l == name[n:n+len(l)]:
#                         # print(name[n:n+len(l)])
#                         front = name[:n+len(l)]
#                         print('front',front)
#                         frontsplit = front.split(" ")
#                         # print('frontsplit',frontsplit)
#                         last_item = frontsplit[-1]
#                         # print('last_item',last_item)
#                         if last_item == '':
#                             frontsplit = frontsplit[:-1] 
#                             frontsentence = frontsplit[-1]
#                         elif last_item == name[n:n+len(l)]:
#                             # print('2')
#                             frontsentence = frontsplit[-2]
#                         elif last_item in frontsplit:
#                             # print('3')
#                             frontsentence = frontsplit[-2]
#                         else:
#                             # print('4')
#                             frontsentence = frontsplit[-1]
                            
                            
#                         # print(frontsentence,'frontsentence')
#                         back = name[n+len(l):]
#                         backsplit = back.split(" ")
#                         # print('back',back)
#                         # print(backsplit)
#                         # print(len(backsplit))
                        
#                         if len(backsplit) == 2:
#                             backsentence = backsplit[1]
#                         elif len(backsplit) == 1:
#                             backsentence = ''
#                         else:
#                             backsentence = backsplit[1]+ " " +backsplit[2]
                            
#                         middlecheck = name[n:n+len(l)]+backsplit[0]
#                         print('middlecheck',middlecheck)
#                         print('name[n:n+len(l)]',name[n:n+len(l)])
#                         if len(middlecheck) == len(name[n:n+len(l)]):
                            
#                             t = frontsplit[-1][:len(frontsplit[-1])-(len(name[n:n+len(l)]))]
#                             # print('frontsplit',frontsplit[-1])
#                             # print(len(frontsplit[-1])-(n+len(l)))
#                             # print('t',t)
#                             # print('frontsplit',frontsplit)
#                             middle = t +'<span style="color:red">'+name[n:n+len(l)]+'</span>'
#                             # frontsentence = frontsplit[-1]
#                         else:
#                             middle = '<span style="color:red">'+name[n:n+len(l)]+'</span>'+backsplit[0]
#                         print('middle',middle)
#                         print('middle',middle)
#                         s = frontsentence + " " + middle + " " +backsentence +'</br>'
#                         # for a in sentence:
#                         if s not in sentence:
#                             sentence.append(s)
                            
        
            
            
            
        
#     # for m in listfull:
#     #     # print(l)
#     #     for l in name:
#     #         # print('name_result[l]',name_result[l])
#     #         # if  m == name_result[l] and name_result[l] != '':
#     #         if any(word.startswith(l) for word in listfull) and l != ' ' and len(l) > 1:
#                 # print(l)
#                 # print(len(l))
#                 # print(name_result[l-1])
#                 # front = name[:name.index(m)]
#                 # frontsplit = front.split(" ")
#                 # for f in frontsplit:
#                 #     last_item = frontsplit[-1]
#                 #     if last_item == '':
#                 #         frontsplit = frontsplit[:-1] 
#                 #     frontsentence = (frontsplit[-1])
#                 #     back = name[name.index(m):]
#                 #     backsplit = back.split(" ")
#                 #     # print('back',backsplit)
#                 #     if len(backsplit) == 2:
#                 #         backsentence = backsplit[1]
#                 #     else:
#                 #         backsentence = backsplit[1]+ " " +backsplit[2]
#                 # # print('frontsplit',frontsplit)
#                 # # print('backsentence',backsentence)
#                 # # print(len(frontsplit))
#                 # # sentence.append(name_result[l-1] + " " + '<span style="color:red">'+name_result[l]+'</span>'+ " " +name_result[l+1]+ " " +name_result[l+2])
#                 # s = frontsentence + " " + '<span style="color:red">'+backsplit[0]+'</span>'+ " " +backsentence
#                 # # for a in sentence:
#                 # if s not in sentence:
#                 #     sentence.append(s)
                
#                 # print(s)
#                 # print(name_result[l])
#                 # print(name_result[l+1])
#     # print(sentence)
    
#     return sentence

@app.route('/checkkeyword')
def checkkeyword():
    name = request.args.get('name')
    # name = name.replace(' ', '')
    # name = 'รายละเอียดสินค้าแท้% Fercy Fiber S เฟอร์ซี่ ไฟเบอร์ เอส Fercy Diet เฟอซี่ไดเอทFercy Diet เฟอร์ซี่ เคล็ดลับหุ่นดี คุมหิว อิ่มนาน น้ำหนักลงง่ายๆ ไม่ต้องอด ช่วยลดความอยากอาหาร ดักจับไขมัน'
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
    
    setting = requests.get('http://localhost:8081/api/token_setting')
    setting = setting.text
    setting = json.loads(setting)
    setting = np.asarray(setting)
    setting_front = int(setting[0]["front_space"])
    setting_back = int(setting[0]["back_space"])
    
    k = ''
    key = []
    for restaurant in keyword_dicts:
        # print (restaurant['name'])
        value = restaurant['name']
        k+=restaurant['name']
        key.append(restaurant['name'])
        words.add(value) 
    
    sentence = []
    backlist = []
    alltext = []
    backsentence = ''
    frontsentence = ''
    # print(listfull)
    for n in range(len(name)):
        for l in key:
            for ll in l:
                # print(ll,'ll')
                # print(name[n],'n')
                if name[n] == ll:
                    # print('name',name[n:n+len(l)])
                    # print(l)
                    if l == name[n:n+len(l)]:
                        # print(l)
                        # print(name[n:n+len(l)])
                        front = name[:n+len(l)]
                        # print('front',front)
                        frontsplit = front.split(" ")
                        # print('frontsplit',frontsplit)
                        last_item = frontsplit[-1]
                        # print('last_item',last_item)
                        frontsplit = [x for x in frontsplit if x]
                        lastnum = int(len(frontsplit))
                        # frontsentence = frontsplit[lastnum-1]
                        frontsentence = ''
                        # print(frontsplit[lastnum-1])
                        if last_item in frontsplit:
                            frontsentence += frontsplit[((lastnum-(setting_front+1)))] +' '
                        
                        for fr in range(setting_front):
                            frontsentence += frontsplit[((lastnum-setting_front)+(fr))] +' '
                            
                        # print('frontsentence',frontsentence)
                        back = name[n+len(l):]
                        backsplit = back.split(" ")
                        backsentence =''
                        # print('back',back)
                        # print(backsplit)
                        # print(len(backsplit))
                        
                        if len(backsplit) == 2:
                            backsentence = backsplit[1]
                        elif len(backsplit) == 1:
                            backsentence = ''
                        else:
                            for sett in range(setting_back):
                                backsentence += backsplit[sett+1] +" "
                                # print(backsentence)
                            # backsentence = backsplit[1]+ " " +backsplit[2]
                            
                        # middlecheck = name[n:n+len(l)]+backsplit[0]
                        # print('middlecheck',middlecheck)
                        # print('name[n:n+len(l)]',name[n:n+len(l)])
                        # if len(middlecheck) == len(name[n:n+len(l)]):
                            
                        #     t = frontsplit[-1][:len(frontsplit[-1])-(len(name[n:n+len(l)]))]
                        #     # print('frontsplit',frontsplit[-1])
                        #     # print(len(frontsplit[-1])-(n+len(l)))
                        #     # print('t',t)
                        #     # print('frontsplit',frontsplit)
                        #     middle = t +'<span style="color:red">'+name[n:n+len(l)]+'</span>'
                        #     # frontsentence = frontsplit[-1]
                        # else:
                        # print(name[n:n+len(l)])
                        # if name[n:n+len(l)] in frontsentence:
                        #     frontsentence = frontsentence.replace(name[n:n+len(l)],'<span style="color:red">'+name[n:n+len(l)]+'</span>')
                        middle = backsplit[0]
                        mi = middle
                        # print('name[n:n+len(l)]',name[n:n+len(l)])
                        # print('frontsentence',frontsentence)
                        # print('frontsentence',frontsentence)
                        # print('middle',middle)
                        # print('backsentence',backsentence)
                        s = frontsentence + middle + " " +backsentence +'</br>'
                        # for a in sentence:
                        
                            
                        arrfront = ''
                        sentences = []
                        # print(len(sentence))
                        if len(sentence) != 0:
                            for se in sentence:
                                # print(se)
                                sen = se.replace('<span style="color:red">','')
                                sen = sen.replace('</span>','')
                                # print('sen',sen)
                                sentences.append(sen)
                                
                        # print('sentences',sentences)
                        # if len(sentences) != 0:
                        
                        # print(backlist)
                        if s not in sentences:
                            # print(s)
                            arr =frontsentence.split()
                            last_front = arr[-1]
                            # print('arr',arr)
                            # print('last_front',last_front)
                            for i in range(len(arr)-1):
                                arrfront += arr[i] + ' '
                                
                            bb = last_front.replace(l,'<span style="color:red">'+l+'</span>')
                            
                            # print('bb',bb)
                                
                            frontsentence = arrfront + bb
                            # print(middle,'middle')
                            for mid in key:
                                middle = middle.replace(mid,'<span style="color:red">'+mid+'</span>')
                            
                            backk = backsentence
                            for kk in key:
                                    backk = backk.replace(kk,'<span style="color:red">'+kk+'</span>')
                                
                            # print(middle,'middle')
                            # frontsentence = frontsentence.replace(name[n:n+len(l)],'<span style="color:red">'+name[n:n+len(l)]+'</span>')
                            s = frontsentence + middle + " " +backk +'</br>'
                            
                            backsens = backsentence.split()
                            
                            # print(backsens)
                            # print(len(backsens),backsens)
                            # print(backsens[1])
                                    # if frontsentence != bac and mi != bac and backsentence != bac:
                            # sentence.append(s)
                            status = 0
                            if len(sentence) > 0:
                                # print('removeback',removeback)
                                fo = frontsentence.replace('<span style="color:red">','')
                                fo = fo.replace('</span>','')
                                # print('fo',fo)
                                # print('mid',mi)
                                # print('backsentence',backsentence)
                               
                                liststr = fo + ' '+mi+' '+backsentence
                                arrstr = liststr.split(" ")
                                arrstr = [x for x in arrstr if x]
                                print('arrstr',arrstr)
                                print('removeback',removeback)
                                
                                for a in arrstr:
                                     if a == removeback:
                                        status = 1
                                # print(status)   
                                if status == 0 :
                                    sentence.append(s)
                                # if removeback != '' and (removeback not in fo or removeback not in mi or removeback not in backsentence):
                                    
                                #     sentence.append(s)
                                        
                            else:
                                sentence.append(s)
                            if len(backsens) != 0:
                                if len(backsens) > 1:
                                    removeback = backsens[1]
                                else:
                                    removeback = backsens[0]
                        
    return sentence


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