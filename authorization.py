# -*- coding: utf-8 -*-

from flask import request
from functools import wraps
from model import token
from datetime import datetime
from util import make_response

rds = None

def INVALID_ACCESS_TOKEN():
    e = {"error":"非法的access token"}
    return make_response(400, e)
def EXPIRE_ACCESS_TOKEN():
    e = {"error":"过期的access token"}
    return make_response(400, e)

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
