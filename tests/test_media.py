#-*- coding: utf-8  -*-
import requests
import base64
import hashlib
import json
import time
import os

APP_ID = 7
APP_KEY = "sVDIlIiDUm7tWPYWhi6kfNbrqui3ez44"
APP_SECRET = '0WiCxAU1jh76SbgaaFC7qIaBPm2zkyM1'


#URL = "http://api.gobelieve.io"
URL = "http://dev.api.gobelieve.io"
URL = "http://localhost:5000"

URL2 = "http://localhost:6000/v2"



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
    obj = {"uid": uid, "user_name": str(uid)}

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
        "sender": sender,
        "receiver": receiver,
        "content": content
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert (r.status_code == 200)



####################################client

def TestDeviceToken():
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "application/json"

    url = URL2 + "/device/bind"
    data = {
        # "ng_device_token":"292854919A9A4E4E1818ABABF2F6ADC9",
        # "xg_device_token":"adb238518d682b2e49cba26c207f04a712c6da46",
        # "xm_device_token":"d//igwEhgBGCI2TG6lWqlOlzU8pu8+C4t+wQ4zMxFYhLO0pHWInlKmKMyW9I3gWgby1Z1vq59TkIQQYeaS43gEzCfwuNRp+OkuHM3JCDA5U=",
        # "hw_device_token":"08650300127619392000000630000001",
        "apns_device_token": "177bbe6da89125b84bfad60ff3d729005792fad4ebbbf5729a8cecc79365a218",
        # "gcm_device_token":"fNMMmCwoba0:APA91bGqpKqwMvbxNlAcGj6wILQoCAY59wx3huFculEkUyElnidJvuEgwVVFuD3PKBUoLIop8ivJlXlkJNPYfFAnabHPAn8_o4oeX1b8eIaOQLmVOkXY-sUw-QAY4MF9PG4RL3TDq7e6",
        # "jp_device_token":"111111",
        # "pushkit_device_token":"144c67f2fde4b72de8ed4203e9672c064e12376ed340d55f8e04430e15ad5a47"
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert (r.status_code == 200)

    content = json.dumps({"text": "test"})
    send_message(2000, 1000, content)
    time.sleep(1)

    url = URL2 + "/device/unbind"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert (r.status_code == 200)



def TestImage():
    url = URL2 + "/images"
    files = {'file': ('test.jpg', open('data/test.jpg', 'rb'), "image/jpeg")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    assert (r.status_code == 200)
    image_url = json.loads(r.text)["src_url"]
    print("image url:", image_url)

    origin_size = os.stat("data/test.jpg").st_size
    r = requests.get(image_url, headers=headers)
    assert (r.status_code == 200)
    print("origin image len:", origin_size, "image len:", len(r.content))

    url = image_url + "@128w_128h_1c.jpg"
    r = requests.get(url, headers=headers)
    assert (r.status_code == 200)
    print("cut image 128*128 len:", len(r.content))
    f = open("/tmp/tt.jpg", "wb")
    f.write(r.content)
    f.close()

    url = image_url + "@128w_128h_0c.jpg"
    r = requests.get(url, headers=headers)
    assert (r.status_code == 200)
    print("image 128*128 len:", len(r.content))
    f = open("/tmp/tt2.jpg", "wb")
    f.write(r.content)
    f.close()



def TestAudio():
    url = URL2 + "/audios"
    files = {'file': ('test.amr', open('data/test.amr', 'rb'), "application/plain")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    assert (r.status_code == 200)
    audio_url = json.loads(r.text)["src_url"]
    print("audio url:", audio_url)

    origin_size = os.stat("data/test.amr").st_size
    r = requests.get(audio_url, headers=headers)
    assert (r.status_code == 200)
    print("origin audio len:", origin_size, "audio len:", len(r.content))

    if False:
        url = audio_url + ".mp3"
        r = requests.get(url, headers=headers)
        assert (r.status_code == 200)
        print("mp3 len:", len(r.content))


def TestFile():
    url = URL2 + "/files"

    files = {'file': ('test.amr', open('data/test.amr', 'rb'), "application/plain")}
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    r = requests.post(url, headers=headers, files=files)
    print(r.status_code, r.content)


access_token = login(1)
print("token:", access_token)
TestFile()
TestImage()
TestAudio()
TestDeviceToken()
