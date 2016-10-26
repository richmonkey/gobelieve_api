# -*- coding: utf-8 -*-
import config
from urllib import urlencode
from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
import random
from libs.crossdomain import crossdomain
from libs.util import make_response
from libs.util import create_access_token
from libs.response_meta import ResponseMeta
from authorization import require_application_or_person_auth
from authorization import require_application_auth
from authorization import require_auth
from authorization import require_client_auth
from models.user import User
from models.app import App
from models.customer import Customer
from rpc import init_message_queue

app = Blueprint('user', __name__)


def publish_message(rds, channel, msg):
    rds.publish(channel, msg)

@app.route("/auth/grant", methods=["POST"])
@require_application_auth
def grant_auth_token():
    rds = g.rds
    appid = request.appid
    obj = json.loads(request.data)
    uid = obj["uid"]
    name = obj["user_name"] if obj.has_key("user_name") else ""
    token = User.get_user_access_token(rds, appid, uid)
    if not token:
        token = create_access_token()
        User.add_user_count(rds, appid, uid)

    User.save_user_access_token(rds, appid, uid, name, token)

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

@app.route("/users/<int:uid>", methods=["POST"])
@require_application_auth
def set_user_name(uid):
    rds = g.rds
    appid = request.appid
    obj = json.loads(request.data)
    name = obj["name"] if obj.has_key("name") else ""
    if name:
        User.set_user_name(rds, appid, uid, name)
    elif obj.has_key('forbidden'):
        #聊天室禁言
        fb = 1 if obj['forbidden'] else 0
        User.set_user_forbidden(rds, appid, uid, fb)
        content = "%d,%d,%d"%(appid, uid, fb)
        publish_message(rds, "speak_forbidden", content)
    else:
        raise ResponseMeta(400, "invalid param")

    return ""
