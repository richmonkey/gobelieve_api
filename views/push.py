# -*- coding: utf-8 -*-
import config
from urllib import urlencode
from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
from libs.util import make_json_response
from libs.response_meta import ResponseMeta
from authorization import require_auth
from models.user import User

app = Blueprint('push', __name__)


@app.route("/device/bind", methods=["POST"])
@require_auth
def bind_device_token():
    rds = g.rds
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

    if not device_token and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")


    User.save_user_device_token(rds, appid, uid, device_token, 
                                ng_device_token, xg_device_token,
                                xm_device_token, hw_device_token,
                                gcm_device_token, jp_device_token)
    return make_json_response({"success":True}, 200)

@app.route("/device/unbind", methods=["POST"])
@require_auth
def unbind_device_token():
    rds = g.rds
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

    if not device_token and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")

    User.reset_user_device_token(rds, appid, uid, device_token, 
                                 ng_device_token, xg_device_token, 
                                 xm_device_token, hw_device_token,
                                 gcm_device_token, jp_device_token)

    return make_json_response({"success":True}, 200)
