#-*- coding: utf-8  -*-
import requests
import base64
import hashlib
import json

APP_ID = 7
APP_KEY = "sVDIlIiDUm7tWPYWhi6kfNbrqui3ez44"
APP_SECRET = '0WiCxAU1jh76SbgaaFC7qIaBPm2zkyM1'


#URL = "http://api.gobelieve.io"
URL = "http://dev.api.gobelieve.io"
URL = "http://localhost:5000"


def md5(s):
    return hashlib.md5(s.encode(encoding='utf8')).hexdigest()


def gen_auth_headers():
    secret = md5(APP_SECRET)
    basic = base64.b64encode((str(APP_ID) + ":" + secret).encode(encoding='utf8'))
    basic = basic.decode("utf-8")
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
    return headers


auth_headers = gen_auth_headers()


def login(uid):
    url = URL + "/auth/grant"
    obj = {"uid":uid, "user_name":str(uid)}

    headers = auth_headers
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    if res.status_code != 200:
        print(res.status_code, res.content)
        return None
    obj = json.loads(res.text)
    return obj["data"]["token"]




    
def send_message(sender, receiver, content):
    url = URL + "/messages/peers"
    
    headers = auth_headers
    data = {
        "sender":sender,
        "receiver":receiver,
        "content":content
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)


def TestRoomMessage():
    url = URL + "/messages/rooms"

    headers = auth_headers    

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
    print("send room message success")
    
def TestGroupNotification():
    url = URL + "/messages/groups/notifications"
    
    headers = auth_headers

    notification = json.dumps({"text":"hello"})
    data = {
        "group_id":2778,
        "content":notification
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("send group notification success")

    

def TestForbidden():
    uid = 1000
    url = URL + "/users/%s"%uid

    headers = auth_headers
    data = {"forbidden":True}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set forbidden:1 success")

    data = {"forbidden":False}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set forbidden:0 success")


def TestDoNotDisturb():
    uid = 1000
    url = URL + "/users/%s"%uid

    headers = auth_headers        

    data = {"do_not_disturb":{"peer_uid":100, "on":True}}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set do not disturb:1 success")

    data = {"do_not_disturb":{"peer_uid":100, "on":False}}    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set do not disturb:0 success")



#pc在线，手机静音选项
def TestMute():
    uid = 1000
    url = URL + "/users/%s"%uid

    headers = auth_headers
    data = {"mute":True}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set mute:1 success")

    data = {"mute":False}    
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("set mute:0 success")


def TestUserName():
    headers = auth_headers
    url = URL + "/users/200"
    data = {
        "name":"测试用户200"
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)


access_token = login(1)
print("token:", access_token)

TestRoomMessage()
TestForbidden()
TestDoNotDisturb()
TestMute()
TestGroupNotification()


