# -*- coding: utf-8 -*-

from flask import request
from flask import g
from functools import wraps
from libs.util import make_response
import logging
import random
import time
import json
import hashlib
import base64
import config


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
    meta = {"message":"非法的access token", "code":400}
    e = {"error":"非法的access token", "meta":meta}
    logging.warning("非法的access token")
    return make_response(400, e)

def INVALID_APPID():
    meta = {"message":"非法的appid", "code":400}
    e = {"meta":meta}
    logging.warning("非法的appid")
    return make_response(400, e)

def INVALID_IP():
    meta = {"message":"非法的ip", "code":400}
    e = {"meta":meta}
    return make_response(400, e)

def INVALID_AUTHORIZATION():
    meta = {"message":"非法的authorization", "code":400}
    e = {"meta":meta}
    logging.warning("非法的authorization")
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
        if not t.load(g.rds, tok):
            return INVALID_ACCESS_TOKEN()
        request.uid = int(t.user_id)
        request.appid = int(t.app_id)
        return f(*args, **kwargs)
    return wrapper
  
def get_app_secret(db, appid):
    if hasattr(config, "APPID") and hasattr(config, "APPSECRET"):
        if config.APPID == appid:
            return config.APPSECRET
        
    sql = "SELECT `key`, secret FROM app WHERE id=%s"
    cursor = db.execute(sql, appid)
    obj = cursor.fetchone()
    return obj["secret"]

def get_app_key(db, appid):
    if hasattr(config, "APPID") and hasattr(config, "APPKEY"):
        if config.APPID == appid:
            return config.APPKEY

    sql = "SELECT `key`, secret FROM app WHERE id=%s"
    cursor = db.execute(sql, appid)
    obj = cursor.fetchone()
    return obj["key"]

def require_application_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            basic = request.headers.get('Authorization')[6:]
        else:
            return INVALID_APPID()
        logging.debug("basic:%s", basic)
        basic = base64.b64decode(basic)
        basic = basic.decode("utf-8")
        sp = basic.split(":", 1)
        if len(sp) != 2:
            return INVALID_APPID()
        appid = int(sp[0])
        appsecret = sp[1]
        secret = get_app_secret(g._db, appid)
        m = hashlib.md5()
        m.update(secret.encode(encoding='UTF-8'))
        secret = m.hexdigest()
        logging.debug("app secret:%s, %s", appsecret, secret)
        if appsecret.lower() != secret.lower():
            return INVALID_APPID()
        ip = request.headers.get('X-Real-IP')
        if ip and appid in config.IP_PERMISSIONS:
            if ip not in config.IP_PERMISSIONS[appid]:
                logging.warning("非法的ip:%s", ip)
                return INVALID_IP()

        request.appid = appid
        return f(*args, **kwargs)
    return wrapper


def require_application_or_person_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            auth = request.headers.get('Authorization')
        else:
            return INVALID_AUTHORIZATION()

        if auth[:6] == "Basic ":
            basic = auth[6:]
            basic = base64.b64decode(basic)
            basic = basic.decode()
            sp = basic.split(":", 1)
            if len(sp) != 2:
                return INVALID_APPID()
            appid = int(sp[0])
            appsecret = sp[1]
            secret = get_app_secret(g._db, appid)
            m = hashlib.md5()
            m.update(secret.encode(encoding='UTF-8'))
            secret = m.hexdigest()
            logging.debug("app secret:%s, %s", appsecret, secret)
            if appsecret.lower() != secret.lower():
                return INVALID_APPID()
            request.appid = appid
            return f(*args, **kwargs)
        elif auth[:7] == "Bearer ":
            tok = auth[7:]
            t = AccessToken()
            if not t.load(g.rds, tok):
                return INVALID_ACCESS_TOKEN()
            request.uid = int(t.user_id)
            request.appid = int(t.app_id)
            return f(*args, **kwargs)
        else:
            return INVALID_AUTHORIZATION()

    return wrapper
    
def require_client_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            basic = request.headers.get('Authorization')[6:]
        else:
            return INVALID_APPID()
        basic = base64.b64decode(basic)
        basic = basic.decode()
        sp = basic.split(":", 1)
        if len(sp) != 2:
            return INVALID_APPID()
        appid = int(sp[0])
        appkey = sp[1]

        dbAppKey = get_app_key(g._db, appid)
        if dbAppKey.lower() != appkey.lower():
            return INVALID_APPID()

        logging.debug("appid:%s appkey:%s", appid, appkey)
        request.appid = appid
        return f(*args, **kwargs)
    return wrapper
    
