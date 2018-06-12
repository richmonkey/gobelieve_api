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
from authorization import require_application_auth
from models.group_model import Group
from models.user import User

from libs.util import make_response
from libs.response_meta import ResponseMeta
from rpc import send_group_notification

app = Blueprint('group', __name__)

publish_message = Group.publish_message
        
@app.route("/groups", methods=["POST"])
@require_application_auth
def create_group():
    appid = request.appid
    obj = json.loads(request.data)
    master = obj["master"]
    name = obj["name"]
    is_super = obj["super"] if obj.has_key("super") else False
    members = obj["members"]

    if hasattr(request, 'uid') and request.uid != master:
        raise ResponseMeta(400, "master must be self")
        
    gid = 0
    if config.EXTERNAL_GROUP_ID:
        gid = obj['group_id'] if obj.has_key('group_id') else 0

    #支持members参数为对象数组
    #[{uid:"", name:"", avatar:"可选"}, ...]
    memberIDs = map(lambda m:m['uid'] if type(m) == dict else m, members)
    
    if gid > 0:
        gid = Group.create_group_ext(g._db, gid, appid, master, name, 
                                     is_super, memberIDs)
    else:
        gid = Group.create_group(g._db, appid, master, name, 
                                 is_super, memberIDs)
    
    s = 1 if is_super else 0
    content = "%d,%d,%d"%(gid, appid, s)
    publish_message(g.rds, "group_create", content)
    
    for mem in memberIDs:
        content = "%d,%d"%(gid, mem)
        publish_message(g.rds, "group_member_add", content)
    
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



@app.route("/groups/<int:gid>", methods=["DELETE"])
@require_application_auth
def delete_group(gid):
    appid = request.appid
    Group.disband_group(g._db, gid)

    v = {
        "group_id":gid,
        "timestamp":int(time.time())
    }
    op = {"disband":v}
    send_group_notification(appid, gid, op, None)

    content = "%d"%gid
    publish_message(g.rds, "group_disband", content)

    resp = {"success":True}
    return make_response(200, resp)



@app.route("/groups/<int:gid>/upgrade", methods=["POST"])
@require_application_auth
def upgrade_group(gid):
    """从普通群升级为超级群"""
    appid = request.appid
    group = Group.get_group(g._db, gid)

    members = Group.get_group_members(g._db, gid)

    if not group:
        raise ResponseMeta(400, "group non exists")

    Group.update_group_super(g._db, gid, 1)

    content = "%d,%d,%d"%(gid, appid, 1)
    publish_message(g.rds, "group_upgrade", content)

    v = {
        "group_id":gid,
        "timestamp":int(time.time()),
        "super":1
    }
    op = {"upgrade":v}
    send_group_notification(appid, gid, op, None)

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>", methods=["PATCH"])
@require_application_auth
def update_group(gid):
    appid = request.appid
    obj = json.loads(request.data)
    name = obj["name"]
    Group.update_group_name(g._db, gid, name)

    v = {
        "group_id":gid,
        "timestamp":int(time.time()),
        "name":name
    }
    op = {"update_name":v}
    send_group_notification(appid, gid, op, None)

    return ""

@app.route("/groups/<int:gid>/members", methods=["POST"])
@require_application_auth
def add_group_member(gid):
    appid = request.appid
    obj = json.loads(request.data)
    if type(obj) is dict:
        members = [obj]
    else:
        members = obj

    if len(members) == 0:
        return ""

    #支持members参数为对象数组
    memberIDs = map(lambda m:m['uid'] if type(m) == dict else m, members)
    
    g._db.begin()
    for member_id in memberIDs:
        try:
            Group.add_group_member(g._db, gid, member_id)
        except umysql.SQLError, e:
            #1062 duplicate member
            if e[0] != 1062:
                raise

    g._db.commit()

    for m in members:
        member_id = m['uid'] if type(m) == dict else m
        v = {
            "group_id":gid,
            "member_id":member_id,
            "timestamp":int(time.time())
        }
        if type(m) == dict and m.get('name'):
            v['name'] = m['name']
        if type(m) == dict and m.get('avatar'):
            v['avatar'] = m['avatar']
        
        op = {"add_member":v}
        send_group_notification(appid, gid, op, [member_id])
         
        content = "%d,%d"%(gid, member_id)
        publish_message(g.rds, "group_member_add", content)

    resp = {"success":True}
    return make_response(200, resp)


def remove_group_member(appid, gid, member):
    memberid = member['uid']    
    Group.delete_group_member(g._db, gid, memberid)
         
    v = {
        "group_id":gid,
        "member_id":memberid,
        "timestamp":int(time.time())
    }
    if member.get('name'):
        v['name'] = member['name']
    if member.get('avatar'):
        v['avatar'] = member['avatar']
    
    op = {"quit_group":v}
    send_group_notification(appid, gid, op, [memberid])
     
    content = "%d,%d"%(gid,memberid)
    publish_message(g.rds, "group_member_remove", content)
    
@app.route("/groups/<int:gid>/members/<int:memberid>", methods=["DELETE"])
@require_application_auth
def leave_group_member(gid, memberid):
    appid = request.appid
    if hasattr(request, "uid") and request.uid > 0:
        #群组管理员或者成员本身有权限退出群
        if memberid != request.uid:
            master = Group.get_group_master(g._db, gid)
            if master != request.uid:
                raise ResponseMeta(400, "no authority")


    remove_group_member(appid, gid, {"uid":memberid})

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members", methods=["DELETE"])
@require_application_auth
def delete_group_member(gid):
    appid = request.appid
    if hasattr(request, "uid") and request.uid > 0:
        #群组管理员或者成员本身有权限退出群
        master = Group.get_group_master(g._db, gid)
        if master != request.uid:
            raise ResponseMeta(400, "no authority")

    members = json.loads(request.data)
    if len(members) == 0:
        raise ResponseMeta(400, "no memebers to delete")

    for m in members:
        if type(m) == int:
            member = {"uid":m}
        else:
            member = m
            
        remove_group_member(appid, gid, member)

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members/<int:memberid>", methods=["PATCH"])
@require_application_auth
def group_member_setting(gid, memberid):
    appid = request.appid
    uid = memberid
    
    obj = json.loads(request.data)
    if obj.has_key('do_not_disturb'):
        User.set_group_do_not_disturb(g.rds, appid, uid, gid, obj['do_not_disturb'])
    elif obj.has_key('nickname'):
        Group.update_nickname(g._db, gid, uid, obj['nickname'])
        v = {
            "group_id":gid,
            "timestamp":int(time.time()),
            "nickname":obj['nickname'],
            "member_id":uid
        }
        op = {"update_member_nickname":v}
        send_group_notification(appid, gid, op, None)        
    else:
        raise ResponseMeta(400, "no action")

    resp = {"success":True}
    return make_response(200, resp)
