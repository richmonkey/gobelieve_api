import requests
import urllib
import urllib2
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import json
import sys

URL = "http://192.168.33.10:5000"

url = URL + "/verify_code?"
NUMBER = "13635273142"
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

sys.exit(1)

url = URL + "/images"
f = open("/tmp/test.jpg", "rb")
data = f.read()
headers = {}
headers["Authorization"] = "Bearer " + access_token
r = requests.post(url, data=data, headers = headers)
assert(r.status_code == 200)
image_url = json.loads(r.text)["src_url"]
print "image url:", image_url

r = requests.get(image_url, headers = headers)
assert(r.status_code == 200)
print "image len:", len(r.content)

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


