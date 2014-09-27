# -*- coding: utf-8 -*-
from flask import request, Blueprint
import random
import json
import time
import requests
import urllib
import logging
from datetime import datetime
from functools import wraps
from util import make_response
from model import code
from model import token
from model import user

app = Blueprint('auth', __name__)
rds = None

def OVERFLOW():
    e = {"error":"get verify code exceed the speed rate"}
    return make_response(400, e)

def INVALID_PARAM():
    e = {"error":"非法输入"}
    return make_response(400, e)

def INVALID_CODE():
    e = {"error":"验证码错误"}
    return make_response(400, e)

def SMS_FAIL():
    e = {"error":"发送短信失败"}
    return make_response(400, e)
    
    
def INVALID_REFRESH_TOKEN():
    e = {"error":"非法的refresh token"}
    return make_response(400, e)
    
def create_verify_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def check_verify_rate(zone, number):
    now = int(time.time())
    _, ts, count = code.get_verify_code(rds, zone, number)
    if count > 10 and now - ts > 30*60:
        return True
    if now - ts > 50:
        return True

    return False


def send_sms(phone_number, code):
    #短信模版1
    c = " 尊敬的用户,您的注册验证码是%s,感谢您使用%s！"%(code, "羊蹄甲")
    content = "推立方测试%s"%c

    param = {}
    param["k"] = "098b460ba826e1f503e50ead09dc5059"
    param["p"] = "1"
    param["t"] = phone_number
    param["c"] = content

    URL = "http://tui3.com/api/send/?"
    url = URL + urllib.urlencode(param)

    resp = requests.get(url)
    if resp.status_code != 200:
        logging.warning("send sms err status code:%d", resp.status_code)
        return False

    try:
        obj = json.loads(resp.text)
        if obj["err_code"] != 0:
            logging.warning("send sms err:%s", resp.text)
            return False
    except Exception, e:
        logging.warning("resp:%s exception:%s", resp.text, str(e))
        return False

    logging.info("send sms success phone:%s code:%s", phone_number, code)
    return True


@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    zone = request.args.get("zone", "")
    number = request.args.get("number", "")
    logging.info("zone:%s number:%s", zone, number)
    if not check_verify_rate(zone, number):
        return OVERFLOW()
        
    vc = create_verify_code()
    code.set_verify_code(rds, zone, number, vc)
    data = {}
    if True:#debug
        data["code"] = vc
        data["number"] = number
        data["zone"] = zone


    if number == "13800000000":
        return make_response(200, data = data)
        
    if not send_sms(number, vc):
        return SMS_FAIL()

    return make_response(200, data = data)

@app.route("/auth/token", methods=["POST"])
def access_token():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    c1 = obj["code"]
    number = obj["number"]
    zone = obj["zone"]
    apns_device_token = obj["apns_device_token"] if obj.has_key("apns_device_token") else None

    if zone == "86" and number == "13800000000":
        pass
    else:
        c2, timestamp, _ = code.get_verify_code(rds, zone, number)
        if c1 != c2:
            return INVALID_CODE()

    uid = user.make_uid(zone, number)
    u0 = user.get_user(rds, uid)
    u = user.User()
    u.uid = uid
    u.apns_device_token = apns_device_token
    if u0 is None:
        u.state = "Hey!"
    else:
        u.state = u0.state
    user.save_user(rds, u)

    tok = create_token(3600, True)
    t = token.Token(**tok)
    t.user_id = uid
    t.save(rds)
    tok['uid'] = uid
    return make_response(200, tok)


@app.route("/auth/refresh_token", methods=["POST"])
def refresh_token():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    tok = obj["refresh_token"]
    rt = token.RefreshToken()
    if not rt.load(rds, tok):
        return INVALID_REFRESH_TOKEN()

    tok = create_token(3600, True)
    t = token.Token(**tok)
    t.user_id = rt.user_id
    t.save(rds)
    
    
    return make_response(200, tok)

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

def random_token_generator(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))

def create_token(expires_in, refresh_token=False):
    """Create a BearerToken, by default without refresh token."""

    token = {
        'access_token': random_token_generator(),
        'expires_in': expires_in,
        'token_type': 'Bearer',
    }
    if refresh_token:
        token['refresh_token'] = random_token_generator()

    return token
