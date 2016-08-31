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
import umysql
from authorization import require_application_or_person_auth
from authorization import require_auth
from models.group_model import Group
from models.user_model import User

from libs.util import make_response
from libs.response_meta import ResponseMeta
from rpc import send_group_notification

app = Blueprint('group', __name__)

im_url=config.IM_RPC_URL

rds = None

def publish_message(channel, msg):
    rds.publish(channel, msg)

        
@app.route("/groups", methods=["POST"])
@require_application_or_person_auth
def create_group():
    appid = request.appid
    obj = json.loads(request.data)
    master = obj["master"]
    name = obj["name"]
    is_super = obj["super"] if obj.has_key("super") else False
    members = obj["members"]

    if hasattr(request, 'uid') and request.uid != master:
        raise ResponseMeta(400, "master must be self")
        
    gid = obj['group_id'] if obj.has_key('group_id') else 0
    if gid > 0:
        gid = Group.create_group_ext(g._imdb, gid, appid, master, name, 
                                     is_super, members)
    else:
        gid = Group.create_group(g._imdb, appid, master, name, 
                                 is_super, members)
    
    s = 1 if is_super else 0
    content = "%d,%d,%d"%(gid, appid, s)
    publish_message("group_create", content)
    
    for mem in members:
        content = "%d,%d"%(gid, mem)
        publish_message("group_member_add", content)
    
    v = {
        "group_id":gid, 
        "master":master, 
        "name":name, 
        "members":members,
        "timestamp":int(time.time())
    }
    op = {"create":v}
    send_group_notification(appid, gid, op, members)

    resp = {"data":{"group_id":gid}}
    return make_response(200, resp)

#获取群名称,群成员,个人的群设置
@app.route("/groups/<int:gid>", methods=["GET"])
@require_auth
def get_group(gid):
    appid = request.appid
    uid = request.uid

    obj = Group.get_group(g._imdb, gid)
    members = Group.get_group_members(g._imdb, gid)
    for m in members:
        name = User.get_user_name(rds, appid, uid)
        m['name'] = name if name else ''
    obj['members'] = members

    q = User.get_user_notification_quiet(rds, appid, uid, gid)
    obj['quiet'] = bool(q)

    resp = {"data":obj}
    return make_response(200, resp)


#获取个人的所有群组
@app.route("/groups", methods=["GET"])
@require_auth
def get_groups():
    appid = request.appid
    uid = request.uid

    groups = Group.get_groups(g._imdb, appid, uid)
    fields = request.args.get("fields", '')

    fields = fields.split(",")
    for obj in groups:
        gid = obj['id']
        if "members" in fields:
            members = Group.get_group_members(g._imdb, gid)
            for m in members:
                name = User.get_user_name(rds, appid, uid)
                m['name'] = name if name else ''
            obj['members'] = members
     
        if "quiet" in fields:
            q = User.get_user_notification_quiet(rds, appid, uid, gid)
            obj['quiet'] = bool(q)
        
    resp = {"data":groups}
    return make_response(200, resp)

@app.route("/groups/<int:gid>", methods=["DELETE"])
@require_application_or_person_auth
def delete_group(gid):
    appid = request.appid
    Group.disband_group(g._imdb, gid)

    v = {
        "group_id":gid,
        "timestamp":int(time.time())
    }
    op = {"disband":v}
    send_group_notification(appid, gid, op, None)

    content = "%d"%gid
    publish_message("group_disband", content)

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>", methods=["PATCH"])
@require_application_or_person_auth
def update_group(gid):
    appid = request.appid
    obj = json.loads(request.data)
    name = obj["name"]
    Group.update_group_name(g._imdb, gid, name)

    v = {
        "group_id":gid,
        "timestamp":int(time.time()),
        "name":name
    }
    op = {"update_name":v}
    send_group_notification(appid, gid, op, None)

    return ""

@app.route("/groups/<int:gid>/members", methods=["POST"])
@require_application_or_person_auth
def add_group_member(gid):
    appid = request.appid
    obj = json.loads(request.data)
    if type(obj) is dict:
        members = [obj["uid"]]
    else:
        members = obj

    if len(members) == 0:
        return ""

    g._imdb.begin()
    for member_id in members:
        try:
            Group.add_group_member(g._imdb, gid, member_id)
        except umysql.SQLError, e:
            #1062 duplicate member
            if e[0] != 1062:
                raise

    g._imdb.commit()

    for member_id in members:
        v = {
            "group_id":gid,
            "member_id":member_id,
            "timestamp":int(time.time())
        }
        op = {"add_member":v}
        send_group_notification(appid, gid, op, [member_id])
         
        content = "%d,%d"%(gid, member_id)
        publish_message("group_member_add", content)

    resp = {"success":True}
    return make_response(200, resp)


def remove_group_member(appid, gid, memberid):
    Group.delete_group_member(g._imdb, gid, memberid)
         
    v = {
        "group_id":gid,
        "member_id":memberid,
        "timestamp":int(time.time())
    }
    op = {"quit_group":v}
    send_group_notification(appid, gid, op, [memberid])
     
    content = "%d,%d"%(gid,memberid)
    publish_message("group_member_remove", content)
    
@app.route("/groups/<int:gid>/members/<int:memberid>", methods=["DELETE"])
@require_application_or_person_auth
def leave_group_member(gid, memberid):
    appid = request.appid
    if hasattr(request, "uid") and request.uid > 0:
        #群组管理员或者成员本身有权限退出群
        if memberid != request.uid:
            master = Group.get_group_master(g._imdb, gid)
            if master != request.uid:
                raise ResponseMeta(400, "no authority")


    remove_group_member(appid, gid, memberid)

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members", methods=["DELETE"])
@require_application_or_person_auth
def delete_group_member(gid):
    appid = request.appid
    if hasattr(request, "uid") and request.uid > 0:
        #群组管理员或者成员本身有权限退出群
        master = Group.get_group_master(g._imdb, gid)
        if master != request.uid:
            raise ResponseMeta(400, "no authority")

    members = json.loads(request.data)
    if len(members) == 0:
        raise ResponseMeta(400, "no memebers to delete")

    for memberid in members:
        remove_group_member(appid, gid, memberid)

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members/<int:memberid>", methods=["PATCH"])
@require_auth
def group_member_setting(gid, memberid):
    appid = request.appid
    uid = request.uid

    if uid != memberid:
        raise ResponseMeta(400, "setting other is forbidden")

    obj = json.loads(request.data)
    if obj.has_key('quiet'):
        #免打扰
        User.set_group_notification_quiet(rds, appid, uid, gid, obj['quiet'])
    else:
        raise ResponseMeta(400, "no action")

    resp = {"success":True}
    return make_response(200, resp)
