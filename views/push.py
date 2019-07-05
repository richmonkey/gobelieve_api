# -*- coding: utf-8 -*-
import config
from urllib.parse import urlencode
from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
from libs.util import make_json_response
from libs.response_meta import ResponseMeta
from .authorization import require_auth
from models.user import User

app = Blueprint('push', __name__)


@app.route("/device/bind", methods=["POST"])
@require_auth
def bind_device_token():
    rds = g.rds
    appid = request.appid
    uid = request.uid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    device_token = obj.get("apns_device_token", "")
    pushkit_device_token = obj.get("pushkit_device_token", "")
    ng_device_token = obj.get("ng_device_token", "")
    xg_device_token = obj.get("xg_device_token", "")
    xm_device_token = obj.get("xm_device_token", "")
    hw_device_token = obj.get("hw_device_token", "")
    gcm_device_token = obj.get("gcm_device_token", "")
    jp_device_token = obj.get("jp_device_token", "")

    if not device_token and not pushkit_device_token \
       and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")


    User.save_user_device_token(rds, appid, uid,
                                device_token, pushkit_device_token,
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
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    device_token = obj.get("apns_device_token", "")
    pushkit_device_token = obj.get("pushkit_device_token", "")
    ng_device_token = obj.get("ng_device_token", "")
    xg_device_token = obj.get("xg_device_token", "")
    xm_device_token = obj.get("xm_device_token", "")
    hw_device_token = obj.get("hw_device_token", "")
    gcm_device_token = obj.get("gcm_device_token", "")
    jp_device_token = obj.get("jp_device_token", "")

    if not device_token and not pushkit_device_token \
       and not ng_device_token and not xg_device_token \
       and not xm_device_token and not hw_device_token \
       and not gcm_device_token and not jp_device_token:
        raise ResponseMeta(400, "invalid param")


    User.reset_user_device_token(rds, appid, uid,
                                 device_token, pushkit_device_token,
                                 ng_device_token, xg_device_token, 
                                 xm_device_token, hw_device_token,
                                 gcm_device_token, jp_device_token)

    return make_json_response({"success":True}, 200)
