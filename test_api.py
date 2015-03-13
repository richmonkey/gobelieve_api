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



URL = "http://dev.demo.gobelieve.io"

url = URL + "/auth/token"
user = {"uid": 1000, "user_name":"test"}
r = requests.post(url, data=json.dumps(user))
assert(r.status_code == 200)
obj = json.loads(r.text)
access_token = obj["token"]
print "token:", access_token

URL = "http://dev.api.gobelieve.io"

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

