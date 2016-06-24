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
from libs.util import make_response
from libs.response_meta import ResponseMeta
from authorization import require_application_or_person_auth
from authorization import require_application_auth
from authorization import require_auth
from models.user_model import User

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


im_url=config.IM_RPC_URL

def init_message_queue(appid, uid, platform_id, device_id):
    obj = {
        "appid":appid,
        "uid":uid,
        "device_id":device_id,
        "platform_id":platform_id
    }

    url = im_url + "/init_message_queue"
    logging.debug("url:%s", url)
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    return res.status_code == 200

@app.route("/auth/grant", methods=["POST"])
@require_application_auth
def grant_auth_token():
    appid = request.appid
    obj = json.loads(request.data)
    uid = obj["uid"]
    name = obj["user_name"] if obj.has_key("user_name") else ""
    bundle_id = obj.get('bundle_id', '')

    token = User.get_user_access_token(rds, appid, uid, bundle_id)
    if not token:
        token = create_access_token()
        User.add_user_count(rds, appid, uid)
    
    User.save_user_access_token(rds, appid, uid, name, token, bundle_id)

    if obj.has_key("platform_id") and obj.has_key("device_id"):
        platform_id = obj['platform_id']
        device_id = obj['device_id']
        s = init_message_queue(appid, uid, platform_id, device_id)
        if s:
            logging.error("init message queue success")
        else:
            logging.error("init message queue fail")
        
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
    jp_device_token = obj["jp_device_token"] if obj.has_key("jp_device_token") else ""

    bundle_id = obj['bundle_id'] if obj.has_key('bundle_id') else ''

    if not device_token and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")


    User.save_user_device_token(rds, appid, uid, device_token, 
                                ng_device_token, xg_device_token,
                                xm_device_token, hw_device_token,
                                gcm_device_token, jp_device_token, 
                                bundle_id)
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
    jp_device_token = obj["jp_device_token"] if obj.has_key("jp_device_token") else ""
    bundle_id = obj['bundle_id'] if obj.has_key('bundle_id') else ''

    if not device_token and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")

    User.reset_user_device_token(rds, appid, uid, device_token, 
                                 ng_device_token, xg_device_token, 
                                 xm_device_token, hw_device_token,
                                 gcm_device_token, jp_device_token,
                                 bundle_id)

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
