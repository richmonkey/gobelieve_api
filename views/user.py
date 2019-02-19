# -*- coding: utf-8 -*-
from flask import request, Blueprint
from flask import g
import json
import hashlib
import logging
from libs.util import make_response
from libs.util import create_access_token
from libs.response_meta import ResponseMeta
from authorization import require_application_auth
from models.user import User

app = Blueprint('user', __name__)


def publish_message(rds, channel, msg):
    rds.publish(channel, msg)


def saslprep(string):
    return string

def ha1(username, realm, password):
    return hashlib.md5(':'.join((username, realm, saslprep(password)))).digest()

def hmac(username, realm, password):
    return ha1(username, realm, password).encode('hex')


@app.route("/auth/grant", methods=["POST"])
@require_application_auth
def grant_auth_token():
    rds = g.rds
    appid = request.appid
    try:
        obj = json.loads(request.data)
    except ValueError, e:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    uid = obj.get('uid')
    if type(uid) != int:
        raise ResponseMeta(400, "invalid param")

    name = obj.get('user_name', "")
    token = User.get_user_access_token(rds, appid, uid)
    if not token:
        token = create_access_token()
        User.add_user_count(rds, appid, uid)

    User.save_user_access_token(rds, appid, uid, name, token)

    u = "%s_%s"%(appid, uid)
    realm = "com.beetle.face"
    key = hmac(u, realm, token)
    User.set_turn_realm_key(rds, realm, u, key)
        
    data = {"data":{"token":token}}
    return make_response(200, data)


@app.route("/users/<int:uid>", methods=["POST", "PATCH"])
@require_application_auth
def user_setting(uid):
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
    elif obj.has_key("do_not_disturb"):
        contact_id = obj['do_not_disturb']['peer_uid']
        on = obj['do_not_disturb']['on']
        User.set_user_do_not_disturb(g.rds, appid, uid,
                                        contact_id, on)
    elif obj.has_key("mute"):
        User.set_mute(rds, appid, uid, obj["mute"])
    else:
        raise ResponseMeta(400, "invalid param")

    return ""
