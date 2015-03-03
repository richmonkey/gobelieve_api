import requests
import urllib
import urllib2
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import threading
import json
import sys

URL = "http://192.168.33.10"
#URL = "http://im.yufeng.me"

url = URL + "/verify_code?"
NUMBER = "13800000000"
values = {'zone' : '86', 'number' : NUMBER}
params = urllib.urlencode(values) 
url += params

r = requests.post(url)
print r.content
resp = json.loads(r.content)

code = resp["code"]
url = URL + "/auth/token"
values = {"zone":"86", "number":NUMBER, "code":code}
data = json.dumps(values)
r = requests.post(url, data=data)
print r.content
resp = json.loads(r.content)

print "access token:", resp["access_token"]
print "refresh token:", resp["refresh_token"]
access_token = resp["access_token"]
refresh_token = resp["refresh_token"]

url = URL + "/auth/refresh_token"
headers = {}
headers["Authorization"] = "Bearer " + access_token
 
values = {"refresh_token":refresh_token}
data = json.dumps(values)
r = requests.post(url, data=data, headers = headers)
print r.content
resp = json.loads(r.content)
 
print "access token:", resp["access_token"]
print "refresh token:", resp["refresh_token"]
access_token = resp["access_token"]
refresh_token = resp["refresh_token"]
 
url = URL + "/users/me"
headers = {}
headers["Authorization"] = "Bearer " + access_token
values = {"state":"xxxx"}
data = json.dumps(values)
r = requests.patch(url, data = data, headers = headers)
print r.status_code
 
 
url = URL + "/users"
headers = {}
headers["Authorization"] = "Bearer " + access_token
 
obj = [{"zone":"86", "number":"13800000009", "name":"test9"},
       {"zone":"86", "number":"13800000001", "name":"test1"}]
r = requests.post(url, data = json.dumps(obj), headers = headers)
print r.status_code
 
r = requests.get(url, headers = headers)
print "users:", r.text

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


url = URL + "/qrcode/session"
r = requests.get(url)
assert(r.status_code == 200)
obj = json.loads(r.content)
sid = obj["sid"]
print "new sid:", sid

def sweep_qrcode():
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    url = URL + "/qrcode/sweep"
    obj = {"sid":sid}
    r = requests.post(url, headers=headers, data=json.dumps(obj))
    print "sweep:", r.status_code
    return

t = threading.Thread(target=sweep_qrcode)
t.start()

url = URL + "/qrcode/login?sid=%s"%sid
r = requests.get(url)
assert(r.status_code == 200)
print "qrcode login success"

t.join()

