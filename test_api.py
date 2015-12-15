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
    r = requests.post(url, data=json.dumps([13635273144,13635273145]), headers = headers)
    assert(r.status_code == 200)


    url = URL + "/groups/%s/members/13635273143"%str(group_id)
    r = requests.delete(url, headers = headers)

    assert(r.status_code == 200)

    url = URL + "/groups/%s"%str(group_id)
    r = requests.delete(url, headers = headers)


    print "test group completed"

TestImage()
TestAudio()
TestGroup()
