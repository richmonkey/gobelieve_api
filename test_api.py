#-*- coding: utf-8  -*-
import requests
import md5
import base64
import urllib
import urllib2
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import threading
import json
import sys
import time

APP_ID = 7
APP_KEY = "sVDIlIiDUm7tWPYWhi6kfNbrqui3ez44"
APP_SECRET = '0WiCxAU1jh76SbgaaFC7qIaBPm2zkyM1'


#URL = "http://api.gobelieve.io"
URL = "http://dev.api.gobelieve.io"


#表单上传图片
def TestFormImage():
    url = URL + "/v2/images"
    files = {'file': ('test.jpg', open('data/test.jpg', 'rb'), "image/jpeg")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    print r.status_code, r.content

def TestImage():
    url = URL + "/images"
    f = open("data/test.jpg", "rb")
    data = f.read()
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "image/jpeg"
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    image_url = json.loads(r.text)["src_url"]
    print "image url:", image_url
     
    r = requests.get(image_url, headers = headers)
    assert(r.status_code == 200)
    print "origin image len:", len(data), "image len:", len(r.content)
     
    url = image_url + "@128w_128h_1c.jpg"
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print "cut image 128*128 len:", len(r.content)
    f = open("/tmp/tt.jpg", "wb")
    f.write(r.content)
    f.close()
     
    url = image_url + "@128w_128h_0c.jpg"
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print "image 128*128 len:", len(r.content)
    f = open("/tmp/tt2.jpg", "wb")
    f.write(r.content)
    f.close()

def TestFormAudio():
    url = URL + "/v2/audios"

    files = {'file': ('test.amr', open('data/test.amr', 'rb'), "application/plain")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    print r.status_code, r.content


    
def TestAudio():
    url = URL + "/audios"
    f = open("data/test.amr", "rb")
    data = f.read()
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "application/plain"
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    audio_url = json.loads(r.text)["src_url"]
    print "audio url:", audio_url
     
    r = requests.get(audio_url, headers = headers)
    assert(r.status_code == 200)
    print "origin audio len:", len(data), "audio len:", len(r.content)
     
    url = audio_url + ".mp3"
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print "mp3 len:", len(r.content)

def TestFile():
    url = URL + "/files"

    files = {'file': ('test.amr', open('data/test.amr', 'rb'), "application/plain")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    print r.status_code, r.content

    
    
def send_message(sender, receiver, content):
    url = URL + "/messages/peers"

    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    data = {
        "sender":sender,
        "receiver":receiver,
        "content":content
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    
    
def TestDeviceToken():
    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    url = URL + "/users/200"
    data = {
        "name":"测试用户200"
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)

    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "application/json"
    
    url = URL + "/device/bind"

    data = {
        #"ng_device_token":"292854919A9A4E4E1818ABABF2F6ADC9",
        #"xg_device_token":"adb238518d682b2e49cba26c207f04a712c6da46",
        #"xm_device_token":"d//igwEhgBGCI2TG6lWqlOlzU8pu8+C4t+wQ4zMxFYhLO0pHWInlKmKMyW9I3gWgby1Z1vq59TkIQQYeaS43gEzCfwuNRp+OkuHM3JCDA5U=",
        #"hw_device_token":"08650300127619392000000630000001",
        #"apns_device_token":"177bbe6da89125b84bfad60ff3d729005792fad4ebbbf5729a8cecc79365a218",
        #"gcm_device_token":"fNMMmCwoba0:APA91bGqpKqwMvbxNlAcGj6wILQoCAY59wx3huFculEkUyElnidJvuEgwVVFuD3PKBUoLIop8ivJlXlkJNPYfFAnabHPAn8_o4oeX1b8eIaOQLmVOkXY-sUw-QAY4MF9PG4RL3TDq7e6",
        #"jp_device_token":"111111",
        #"pushkit_device_token":"144c67f2fde4b72de8ed4203e9672c064e12376ed340d55f8e04430e15ad5a47"
    }
    r = requests.post(url, data=json.dumps(data), headers = headers)
    assert(r.status_code == 200)

    content = json.dumps({"text":"test"})
    send_message(2000, 1000, content)
    time.sleep(1)
    
    url = URL + "/device/unbind"
    r = requests.post(url, data=json.dumps(data), headers = headers)
    assert(r.status_code == 200)

    
def TestRoomMessage():
    url = URL + "/messages/rooms"

    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    content = json.dumps({"text":"hello"})
    uid = 0
    room_id = 100
    data = {
        "sender":uid,
        "receiver":room_id,
        "content":content
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print "send room message success"
    
def TestGroupNotification():
    url = URL + "/messages/groups/notifications"

    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    notification = json.dumps({"text":"hello"})
    data = {
        "group_id":812,
        "content":notification
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print "send group notification success"


def TestForbidden():
    uid = 1000
    url = URL + "/users/%s"%uid

    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    data = {"forbidden":True}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print "set forbidden:1 success"

    data = {"forbidden":False}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print "set forbidden:0 success"

def TestCustomerRegister():
    appid = 7
    uid = 1000
    url = URL + "/customer/register"

    data = {"appid":appid, "uid":uid, "user_name":"测试客服"}

    basic = base64.b64encode(str(APP_ID) + ":" + APP_KEY)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               "Authorization": "Basic " + basic}

    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print "customer register:", r.content


    obj = json.loads(r.content)
    token = obj['data']['token']
    store_id = obj['data']['store_id']

    url = URL + "/supporters"
    params = {"store_id":store_id}

    headers = {}
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json; charset=UTF-8"

    r = requests.get(url, params=params, headers=headers)
    assert(r.status_code == 200)
    print r.content


def TestGetOfflineCount():
    uid = 1
    url = URL + "/messages/offline"

    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}


    params = {"uid":uid}
    r = requests.get(url, params=params, headers=headers)
    print "get offline count:", r.content
    assert(r.status_code == 200)


def login(uid):
    url = URL + "/auth/grant"
    obj = {"uid":uid, "user_name":str(uid)}
    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
     
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    if res.status_code != 200:
        print res.status_code, res.content
        return None
    obj = json.loads(res.text)
    return obj["data"]["token"]


access_token = login(1)
print "token:", access_token

#TestFile()
#TestFormImage()
#TestFormAudio()
#TestImage()
#TestAudio()
#TestDeviceToken()
#TestRoomMessage()
#TestForbidden()
#TestGroupNotification()
#TestCustomerRegister()
#TestGetOfflineCount()

