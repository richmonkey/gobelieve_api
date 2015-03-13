# -*- coding: utf-8 -*-

from flask import request
from functools import wraps
from util import make_response
import logging
import random
import time
import json

rds = None


def access_token_key(token):
    return "access_token_" + token


class AccessToken(object):
    def __init__(self):
        self.user_id = None
        self.app_id = None

    def _load(self, rds, key):
        t = rds.hmget(key, "user_id", "app_id")
        self.user_id, self.app_id = t
        return True if self.user_id else False

    def load(self, rds, token):
        key = access_token_key(token)
        self.access_token = token
        return self._load(rds, key)

def INVALID_ACCESS_TOKEN():
    e = {"error":"非法的access token"}
    logging.warn("非法的access token")
    return make_response(400, e)


def require_auth(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
        else:
            return INVALID_ACCESS_TOKEN()
        t = AccessToken()
        if not t.load(rds, tok):
            return INVALID_ACCESS_TOKEN()
        request.uid = t.user_id
        request.appid = t.app_id
        return f(*args, **kwargs)
    return wrapper
  
