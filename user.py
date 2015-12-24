# -*- coding: utf-8 -*-
import config
import requests
from urllib import urlencode
from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
import random
from util import make_response
from authorization import require_application_or_person_auth
from authorization import require_application_auth
from authorization import require_auth

app = Blueprint('user', __name__)

rds = None

UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

def random_token_generator(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))

def create_access_token():
    return random_token_generator()

#user model
class User(object):
    @staticmethod
    def get_user_access_token(rds, appid, uid):
        key = "users_%d_%d"%(appid, uid)
        token = rds.hget(key, "access_token")
        return token

    @staticmethod
    def load_user_access_token(rds, token):
        key = "access_token_%s"%token
        exists = rds.exists(key)
        if not exists:
            return 0, 0, ""
        uid, appid, name = rds.hget(key, "user_id", "app_id", "user_name")
        return uid, appid, name

    @staticmethod
    def save_user_access_token(rds, appid, uid, name, token):
        pipe = rds.pipeline()

        key = "access_token_%s"%token
        obj = {
            "user_id":uid,
            "user_name":name,
            "app_id":appid
        }
        
        pipe.hmset(key, obj)

        key = "users_%d_%d"%(appid, uid)
        obj = {
            "access_token":token,
            "name":name
        }

        pipe.hmset(key, obj)
        pipe.execute()

        return True

    @staticmethod
    def save_user_device_token(rds, appid, uid, device_token, 
                               ng_device_token, xg_device_token,
                               xm_device_token, hw_device_token,
                               gcm_device_token):
        now = int(time.time())
        key = "users_%d_%d"%(appid, uid)

        if device_token:
            obj = {
                "apns_device_token":device_token,
                "apns_timestamp":now
            }
            rds.hmset(key, obj)
            
        if ng_device_token:
            obj = {
                "ng_device_token":ng_device_token,
                "ng_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xg_device_token:
            obj = {
                "xg_device_token":xg_device_token,
                "xg_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xm_device_token:
            obj = {
                "xm_device_token":xm_device_token,
                "xm_timestamp":now
            }
            rds.hmset(key, obj)

        if hw_device_token:
            obj = {
                "hw_device_token":hw_device_token,
                "hw_timestamp":now
            }
            rds.hmset(key, obj)
        
        if gcm_device_token:
            obj = {
                "gcm_device_token":gcm_device_token,
                "gcm_timestamp":now
            }
            rds.hmset(key, obj)
            
        return True


    #重置(清空)用户已经绑定的devicetoken
    @staticmethod
    def reset_user_device_token(rds, appid, uid, device_token, 
                                ng_device_token, xg_device_token, 
                                xm_device_token, hw_device_token, 
                                gcm_device_token):
        key = "users_%d_%d"%(appid, uid)
        if device_token:
            t = rds.hget(key, "apns_device_token")
            if device_token == t:
                return False
            rds.hdel(key, "apns_device_token")

        if ng_device_token:
            t = rds.hget(key, "ng_device_token")
            if ng_device_token == t:
                return False
            rds.hdel(key, "ng_device_token")
            
        if xg_device_token:
            t = rds.hget(key, "xg_device_token")
            if xg_device_token == t:
                return False
            rds.hdel(key, "xg_device_token")

        if xm_device_token:
            t = rds.hget(key, "xm_device_token")
            if xm_device_token == t:
                return False
            rds.hdel(key, "xm_device_token")

        if hw_device_token:
            t = rds.hget(key, "hw_device_token")
            if hw_device_token == t:
                return False
            rds.hdel(key, "hw_device_token")

        if gcm_device_token:
            t = rds.hget(key, "gcm_device_token")
            if gcm_device_token == t:
                return False
            rds.hdel(key, "gcm_device_token")
        
        return True

    @staticmethod
    def set_user_name(rds, appid, uid, name):
        key = "users_%d_%d"%(appid, uid)
        rds.hset(key, "name", name)

    @staticmethod
    def add_user_count(rds, appid, uid):
        pass


@app.route("/auth/grant", methods=["POST"])
@require_application_auth
def grant_auth_token():
    appid = request.appid
    obj = json.loads(request.data)
    uid = obj["uid"]
    name = obj["user_name"] if obj.has_key("user_name") else ""
    token = User.get_user_access_token(rds, appid, uid)
    if not token:
        token = create_access_token()
        User.add_user_count(rds, appid, uid)

    User.save_user_access_token(rds, appid, uid, name, token)

    data = {"data":{"token":token}}
    return make_response(200, data)

@app.route("/device/bind", methods=["POST"])
@require_auth
def bind_device_token():
    appid = request.appid
    uid = request.uid
    obj = json.loads(request.data)
    device_token = obj["apns_device_token"] if obj.has_key("apns_device_token") else ""
    ng_device_token = obj["ng_device_token"] if obj.has_key("ng_device_token") else ""
    xg_device_token = obj["xg_device_token"] if obj.has_key("xg_device_token") else ""
    xm_device_token = obj["xm_device_token"] if obj.has_key("xm_device_token") else ""
    hw_device_token = obj["hw_device_token"] if obj.has_key("hw_device_token") else ""
    gcm_device_token = obj["gcm_device_token"] if obj.has_key("gcm_device_token") else ""

    if not device_token and not ng_device_token and not xg_device_token and \
       not xm_device_token and not hw_device_token and not gcm_device_token:
        raise ResponseMeta(400, "invalid param")


    User.save_user_device_token(rds, appid, uid, device_token, 
                                ng_device_token, xg_device_token,
                                xm_device_token, hw_device_token,
                                gcm_device_token)
    return ""

@app.route("/device/unbind", methods=["POST"])
@require_auth
def unbind_device_token():
    appid = request.appid
    uid = request.uid
    obj = json.loads(request.data)
    device_token = obj["apns_device_token"] if obj.has_key("apns_device_token") else ""
    ng_device_token = obj["ng_device_token"] if obj.has_key("ng_device_token") else ""
    xg_device_token = obj["xg_device_token"] if obj.has_key("xg_device_token") else ""
    xm_device_token = obj["xm_device_token"] if obj.has_key("xm_device_token") else ""
    hw_device_token = obj["hw_device_token"] if obj.has_key("hw_device_token") else ""
    gcm_device_token = obj["gcm_device_token"] if obj.has_key("gcm_device_token") else ""

    if not device_token and not ng_device_token and not xg_device_token and \
       not xm_device_token and not hw_device_token and not gcm_device_token:
        raise ResponseMeta(400, "invalid param")

    User.reset_user_device_token(rds, appid, uid, device_token, 
                                 ng_device_token, xg_device_token, 
                                 xm_device_token, hw_device_token,
                                 gcm_device_token)

    return ""

@app.route("/users/<int:uid>", methods=["POST"])
@require_application_auth
def set_user_name(uid):
    appid = request.appid
    obj = json.loads(request.data)
    name = obj["name"] if obj.has_key("name") else ""
    if not name:
        raise ResponseMeta(400, "invalid param")

    User.set_user_name(rds, appid, uid, name)
    return ""
