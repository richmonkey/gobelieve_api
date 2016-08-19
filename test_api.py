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


access_token = login(1000)
print "token:", access_token

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


def TestGroup():
    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    url = URL + "/groups"

    group = {"master":13635273142,"members":[13635273142], "name":"test", "super":True}
    r = requests.post(url, data=json.dumps(group), headers = headers)
    assert(r.status_code == 200)
    obj = json.loads(r.content)
    group_id = obj["data"]["group_id"]


    url = URL + "/groups/%s"%str(group_id)
    r = requests.patch(url, data=json.dumps({"name":"test_new"}), headers = headers)
    assert(r.status_code == 200)

    url = URL + "/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps({"uid":13635273143}), headers = headers)
    assert(r.status_code == 200)


    url = URL + "/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps({"uid":13635273143}), headers = headers)
    print r.content
    assert(r.status_code == 200)


    url = URL + "/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps([13635273144,13635273145]), headers = headers)
    assert(r.status_code == 200)


    url = URL + "/groups/%s/members/13635273143"%str(group_id)
    r = requests.delete(url, headers = headers)

    assert(r.status_code == 200)

    url = URL + "/groups/%s"%str(group_id)
    r = requests.delete(url, headers = headers)


    print "test group completed"


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
        "jp_device_token":"111111",
    }
    r = requests.post(url, data=json.dumps(data), headers = headers)
    assert(r.status_code == 200)

    content = json.dumps({"text":"test"})
    send_message(2000, 1000, content)
    time.sleep(1)

    url = URL + "/device/unbind"
    r = requests.post(url, data=json.dumps(data), headers = headers)
    assert(r.status_code == 200)

def TestCustomerService():
    secret = md5.new(APP_SECRET).digest().encode("hex")
    basic = base64.b64encode(str(APP_ID) + ":" + secret)
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    url = URL + "/applications/%s"%APP_ID

    obj = {"customer_service":True}
    r = requests.patch(url, data=json.dumps(obj), headers=headers)
    assert(r.status_code == 200)
    print "enable customer service success"

    obj = {"customer_service_mode":1}
    r = requests.patch(url, data=json.dumps(obj), headers=headers)
    assert(r.status_code == 200)
    print "set customer service mode:3 success"

    url = URL + "/staffs"
    obj = {"staff_uid":100, "staff_name":"客服100"}
    r = requests.post(url, data=json.dumps(obj), headers=headers)
    assert(r.status_code == 200)
    print "add customer service staff success"

    url = URL + "/staffs/%s"%100
    r = requests.delete(url, headers=headers)
    assert(r.status_code == 200)
    print "remove customer service staff success"
    
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



TestImage()
TestAudio()
TestGroup()
TestDeviceToken()
TestCustomerService()
TestRoomMessage()
TestForbidden()
