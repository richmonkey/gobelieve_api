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


@app.route("/users", methods=["POST", "GET"])
@require_auth
def user_contact():
    if request.method == "POST":
        return get_phone_number_users()
    else:
        return get_user_contact()

def get_user_contact():
    uid = request.uid
    contacts = user.get_user_contact_list(rds, uid)
    resp = []
    for contact in contacts:
        u = user.get_user(rds, contact.uid)
        if u is None:
            continue
        obj = {}
        if u.avatar:
            obj["avatar"] = u.avatar
        obj["uid"] = int(contact.uid)
        obj["name"] = contact.name
        resp.append(obj)
    return json.dumps(resp)

def get_phone_number_users():
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    resp = []
    contacts = []
    for o in req:
        uid = user.make_uid(o["zone"], o["number"])
        u = user.get_user(rds, uid)
        obj = {}
        obj["zone"] = o["zone"]
        obj["number"] = o["number"]

        if u is None:
            obj["uid"] = 0
        else:
            contact = user.Contact()
            contact.name = o["name"] if o.has_key("name") else ""
            contact.uid = uid
            contacts.append(contact)
            obj["uid"] = uid
            if u.state:
                obj["state"] = u.state
            if u.avatar:
                obj["avatar"] = u.avatar
            if u.up_timestamp:
                obj["up_timestamp"] = u.up_timestamp
        resp.append(obj)
            
    user.set_user_contact_list(rds, request.uid, contacts)
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
