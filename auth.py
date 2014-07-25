# -*- coding: utf-8 -*-
from flask import request, Blueprint
import random
import json
import time
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
    
def INVALID_REFRESH_TOKEN():
    e = {"error":"非法的refresh token"}
    return make_response(400, e)

def INVALID_ACCESS_TOKEN():
    e = {"error":"非法的access token"}
    return make_response(400, e)
def EXPIRE_ACCESS_TOKEN():
    e = {"error":"过期的access token"}
    return make_response(400, e)
    
def create_verify_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def check_verify_rate(zone, number):
    now = int(time.time())
    _, ts, count = code.get_verify_code(rds, zone, number)
    if count > 10 and now - ts > 30*60:
        return True
    if now - ts > 60:
        return True

    return True#debug
#    return False

def make_uid(zone, number):
    return int(zone+"0"+number)
@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    zone = request.args.get("zone", "")
    number = request.args.get("number", "")
    if not check_verify_rate(zone, number):
        return OVERFLOW()
        
    vc = create_verify_code()
    code.set_verify_code(rds, zone, number, vc)
    data = {}
    if True:#debug
        data["code"] = vc
        data["number"] = number
        data["zone"] = zone
    
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
    c2, timestamp, _ = code.get_verify_code(rds, zone, number)
    if c1 != c2:
        return INVALID_CODE()

    uid = make_uid(zone, number)
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


def require_auth(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
        else:
            return INVALID_ACCESS_TOKEN()
        t = token.AccessToken()
        if not t.load(rds, tok):
            return INVALID_ACCESS_TOKEN()
        if datetime.utcnow() > t.expires:
            print t.expires, datetime.utcnow()
            return EXPIRE_ACCESS_TOKEN()
        request.uid = t.user_id
        return f(*args, **kwargs)
    return wrapper


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



@app.route("/users", methods=["POST"])
@require_auth
def get_phone_number_users():
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    resp = []
    for o in req:
        uid = make_uid(o["zone"], o["number"])
        u = user.get_user(rds, uid)
        obj = {}
        obj["zone"] = o["zone"]
        obj["number"] = o["number"]

        if u is None:
            obj["uid"] = 0
        else:
            obj["uid"] = uid
            if u.state:
                obj["state"] = u.state
            if u.avatar:
                obj["avatar"] = u.avatar
        resp.append(obj)
            
    return make_response(200, resp)
