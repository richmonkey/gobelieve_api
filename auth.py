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
    c2, timestamp, _ = code.get_verify_code(rds, zone, number)
    if c1 != c2:
        return INVALID_CODE()

    tok = create_token(3600, True)
    t = token.Token(**tok)
    t.user_id = int(zone+number)
    t.save(rds)
    return make_response(200, tok)


def require_auth(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
        else:
            tok = request.access_token
        t = token.AccessToken()
        if not t.load(rds, tok):
            return INVALID_ACCESS_TOKEN()
        if datetime.utcnow() > t.expires:
            return EXPIRE_ACCESS_TOKEN()
        request.uid = t.user_id
        return f(*args, **kwargs)
    return wrapper


@app.route("/auth/refresh_token", methods=["POST"])
@require_auth
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

