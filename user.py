# -*- coding: utf-8 -*-

from authorization import require_auth
from functools import wraps
from flask import request, Blueprint
from model import user
import json
import logging
from util import make_response

app = Blueprint('user', __name__)
rds = None

def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn("非法输入")
    return make_response(400, e)

@app.route("/users", methods=["POST"])
@require_auth
def get_phone_number_users():
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    resp = []
    for o in req:
        uid = user.make_uid(o["zone"], o["number"])
        u = user.get_user(rds, uid)
        obj = {}
        obj["zone"] = o["zone"]
        obj["number"] = o["number"]

        if u is None:
            obj["uid"] = 0
        else:
            obj["uid"] = uid
            if u.state:
                obj["state"] = u.state
            if u.avatar:
                obj["avatar"] = u.avatar
            if u.up_timestamp:
                obj["up_timestamp"] = u.up_timestamp
        resp.append(obj)
            
    return make_response(200, resp)

@app.route("/users/me", methods=['PATCH'])
@require_auth
def set_user_property():
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    if req.has_key('state'):
        state = req['state']
        uid = request.uid
        user.set_user_state(rds, uid, state)
        return ""
    elif req.has_key('avatar'):
        avatar = req['avatar']
        uid = request.uid
        user.set_user_avatar(rds, uid, avatar)
        return ""
    else:
        return INVALID_PARAM()
