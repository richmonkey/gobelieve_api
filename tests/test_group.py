#-*- coding: utf-8  -*-
import requests
import hashlib
import base64
#import urllib.request, urllib.error, urllib.parse
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
URL = "http://localhost:5000"
URL2 = "http://localhost:6000"


def md5(s):
    return hashlib.md5(s.encode(encoding='utf8')).hexdigest()


def login(uid):
    url = URL + "/auth/grant"
    obj = {"uid":uid, "user_name":str(uid)}
    secret = md5(APP_SECRET)
    basic = base64.b64encode((str(APP_ID) + ":" + secret).encode(encoding='utf8'))
    basic = basic.decode("utf-8")    
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
     
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    if res.status_code != 200:
        print(res.status_code, res.content)
        return None
    obj = json.loads(res.text)
    return obj["data"]["token"]




def TestClientGroup():
    access_token = login(13635273143)
    print("token:", access_token)
    
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "application/json"

    url = URL2 + "/client/groups"

    group = {"master":13635273143,"members":[{"uid":13635273143, "name":"测试"}], "name":"test", "super":True}
    r = requests.post(url, data=json.dumps(group), headers = headers)
    assert(r.status_code == 200)
    obj = json.loads(r.content)
    group_id = obj["data"]["group_id"]
    print("new group id:", group_id)

    url = URL2 + "/client/groups/%s"%str(group_id)
    r = requests.patch(url, data=json.dumps({"name":"test_new"}), headers = headers)
    assert(r.status_code == 200)
    print("update group name success")

    url = URL2 + "/client/groups/%s"%str(group_id)
    r = requests.patch(url, data=json.dumps({"notice":"test notice"}), headers = headers)
    assert(r.status_code == 200)
    print("update group notice success")

    url = URL2 + "/client/groups/%s/members/%s"%(str(group_id), 13635273143)
    r = requests.patch(url, data=json.dumps({"nickname":"haha"}), headers = headers)
    assert(r.status_code == 200)
    print("update nickname in group success")

    url = URL2 + "/client/groups/%s/members/%s"%(str(group_id), 13635273143)
    r = requests.patch(url, data=json.dumps({"do_not_disturb":True}), headers = headers)
    assert(r.status_code == 200)
    print("update do not disturb success")

    url = URL2 + "/client/groups/%s"%str(group_id)
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print("get group:", r.content)


    url = URL2 + "/client/groups"
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print("get all group:", r.content)
    

    url = URL2 + "/client/groups?fields=members,quiet"
    r = requests.get(url, headers = headers)
    assert(r.status_code == 200)
    print("get all group with members:", r.content)
    

    url = URL2 + "/client/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps([{"uid":13635273142, "name":"测试2"}]), headers = headers)
    assert(r.status_code == 200)

    print("add group member success")

    url = URL2 + "/client/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps([{"uid":13635273142}]), headers = headers)
    assert(r.status_code == 200)
    print("repeat add group member success")


    url = URL2 + "/client/groups/%s/members"%str(group_id)
    r = requests.post(url, data=json.dumps([{"uid":13635273144, "name":"测试1"},{"uid":13635273145, "name":"测试2"}]), headers = headers)
    assert(r.status_code == 200)
    print("add group member success")

    url = URL2 + "/client/groups/%s/members"%str(group_id)
    r = requests.delete(url, headers = headers, data=json.dumps([{"uid":13635273142, "name":"测试"}]))

    assert(r.status_code == 200)
    print("remove group member success")


    url = URL2 + "/client/groups/%s/members/13635273143"%str(group_id)
    r = requests.delete(url, headers = headers)

    assert(r.status_code == 200)

    print("leave group success")

    url = URL2 + "/client/groups/%s"%str(group_id)
    r = requests.delete(url, headers = headers)

    print("disband group success")

    print("test client group completed")

def TestGroup():
    secret = md5(APP_SECRET)
    basic = base64.b64encode((str(APP_ID) + ":" + secret).encode(encoding='utf8'))
    basic = basic.decode("utf-8")
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}

    url = URL + "/groups"

    group = {"master":13635273143,"members":[{"uid":13635273143}], "name":"test", "super":False}
    r = requests.post(url, data=json.dumps(group), headers = headers)
    assert(r.status_code == 200)
    obj = json.loads(r.content)
    group_id = obj["data"]["group_id"]
    print("new group id:", group_id)

    url = URL + "/groups/%s"%str(group_id)
    r = requests.patch(url, data=json.dumps({"name":"test_new"}), headers = headers)
    assert(r.status_code == 200)
    print("update group name success")

    url = URL + "/groups/%s/upgrade"%str(group_id)
    r = requests.post(url, headers = headers)
    assert(r.status_code == 200)
    print("upgrade group success")


    url = URL + "/groups/%s/members"%str(group_id)
    data = json.dumps({"members":[{"uid":13635273142, "name":"13635273142"}], "inviter":{"uid":13635273143, "name":"haha"}})
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)

    print("add group member success")

    url = URL + "/groups/%s/members"%str(group_id)
    data = json.dumps([{"uid":13635273142, "name":"13635273142"}])    
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print("repeat add group member success")


    url = URL + "/groups/%s/members/%s"%(group_id, 13635273142)
    data = json.dumps({"do_not_disturb":True})
    r = requests.patch(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print("set group do not disturb success")
    

    url = URL + "/groups/%s/members/%s"%(group_id, 13635273142)
    data = json.dumps({"nickname":"nnnnn"})
    r = requests.patch(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print("set group member nickname disturb success")

    url = URL + "/groups/%s/members/%s"%(group_id, 13635273142)
    data = json.dumps({"mute":True})
    r = requests.patch(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print("set group member mute success")

    url = URL + "/groups/%s/members/%s"%(group_id, 13635273142)
    data = json.dumps({"mute":False})
    r = requests.patch(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print("set group member unmute success")

    
    url = URL + "/groups/%s/members"%str(group_id)
    data = json.dumps([{"uid":13635273142, "name":"13635273142"}])            
    r = requests.delete(url, headers = headers, data=data)
    assert(r.status_code == 200)
    print("remove group member success")


    url = URL + "/groups/%s/members/13635273143"%str(group_id)
    r = requests.delete(url, headers = headers)
    assert(r.status_code == 200)
    print("leave group success")
    

    url = URL + "/groups/%s"%str(group_id)
    r = requests.delete(url, headers = headers)
    print("disband group success")

    print("test group completed")


TestGroup()
TestClientGroup()
