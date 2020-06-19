#-*- coding: utf-8  -*-
import requests
import base64
import urllib.parse as urlparse
import hashlib
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

#客户端接口


def TestCustomerRegister():
    appid = 7
    uid = 1000
    url = URL2 + "/customer/register"

    data = {"appid":appid, "uid":uid, "user_name":"测试客服"}

    basic = base64.b64encode((str(APP_ID) + ":" + APP_KEY).encode()).decode()
    headers = {'Content-Type': 'application/json; charset=UTF-8',
               "Authorization": "Basic " + basic}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    assert(r.status_code == 200)
    print("customer register:", r.content)


    obj = json.loads(r.content)
    token = obj['data']['token']
    store_id = obj['data']['store_id']

    url = URL2 + "/supporters"
    params = {"store_id":store_id}

    headers = {}
    headers["Authorization"] = "Bearer " + token
    headers["Content-Type"] = "application/json; charset=UTF-8"

    r = requests.get(url, params=params, headers=headers)
    assert(r.status_code == 200)
    print(r.content)

TestCustomerRegister()

