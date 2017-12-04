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
import redis
from authorization import require_application_or_person_auth
from authorization import require_auth
from models.group_model import Group
from models.user import User

from libs.util import make_response
from libs.response_meta import ResponseMeta
from rpc import send_group_notification

app = Blueprint('c_group', __name__, url_prefix="/client")

im_url=config.IM_RPC_URL


publish_message = Group.publish_message

@app.route("/groups", methods=["POST"])
@require_auth
def create_group():
    appid = request.appid
    obj = json.loads(request.data)
    master = obj["master"]
    name = obj["name"]
    is_super = obj["super"] if obj.has_key("super") else False
    members = obj["members"]

    if hasattr(request, 'uid') and request.uid != master:
        raise ResponseMeta(400, "master must be self")

    #支持members参数为对象数组
    #[{uid:"", name:"", avatar:"可选"}, ...]
    memberIDs = map(lambda m:m['uid'] if type(m) == dict else m, members)
            
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

#获取群名称,群成员,个人的群设置
@app.route("/groups/<int:gid>", methods=["GET"])
@require_auth
def get_group(gid):
    appid = request.appid
    uid = request.uid

    obj = Group.get_group(g._db, gid)
    members = Group.get_group_members(g._db, gid)
    for m in members:
        name = User.get_user_name(g.rds, appid, m['uid'])
        m['name'] = name if name else ''
        if not m.get('nickname'):
            m['nickname'] = ""
        
    obj['members'] = members

    q = User.get_group_do_not_disturb(g.rds, appid, uid, gid)
    obj['do_not_disturb'] = bool(q)

    resp = {"data":obj}
    return make_response(200, resp)


#获取个人的所有群组
@app.route("/groups", methods=["GET"])
@require_auth
def get_groups():
    appid = request.appid
    uid = request.uid

    groups = Group.get_groups(g._db, appid, uid)
    fields = request.args.get("fields", '')

    fields = fields.split(",")
    for obj in groups:
        gid = obj['id']
        if "members" in fields:
            members = Group.get_group_members(g._db, gid)
            for m in members:
                name = User.get_user_name(g.rds, appid, m['uid'])
                m['name'] = name if name else ''
                if not m.get('nickname'):
                    m['nickname'] = ""
                    
            obj['members'] = members
     
        if "quiet" in fields:
            q = User.get_group_do_not_disturb(g.rds, appid, uid, gid)
            obj['do_not_disturb'] = bool(q)
        
    resp = {"data":groups}
    return make_response(200, resp)

@app.route("/groups/<int:gid>", methods=["DELETE"])
@require_auth
def delete_group(gid):
    appid = request.appid

    #群组管理员有权限解散群
    master = Group.get_group_master(g._db, gid)
    if master != request.uid:
        raise ResponseMeta(400, "no authority")
    
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


@app.route("/groups/<int:gid>", methods=["PATCH"])
@require_auth
def update_group(gid):
    appid = request.appid
    obj = json.loads(request.data)

    if obj.has_key('name'):
        name = obj["name"]
        Group.update_group_name(g._db, gid, name)
         
        v = {
            "group_id":gid,
            "timestamp":int(time.time()),
            "name":name
        }
        op = {"update_name":v}
        send_group_notification(appid, gid, op, None)
    elif obj.has_key('notice'):
        notice = obj["notice"]
        Group.update_group_notice(g._db, gid, notice)
        v = {
            "group_id":gid,
            "timestamp":int(time.time()),
            "notice":notice
        }
        op = {"update_notice":v}
        send_group_notification(appid, gid, op, None)
    else:
        raise ResponseMeta(400, "patch nothing")
    
    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members", methods=["POST"])
@require_auth
def add_group_member(gid):
    appid = request.appid
    obj = json.loads(request.data)
    if type(obj) is dict:
        members = [obj["uid"]]
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
@require_auth
def leave_group(gid, memberid):
    appid = request.appid
    #群组管理员或者成员本身有权限退出群
    if memberid != request.uid:
        raise ResponseMeta(400, "no authority")

    remove_group_member(appid, gid, {"uid":memberid})

    resp = {"success":True}
    return make_response(200, resp)


@app.route("/groups/<int:gid>/members", methods=["DELETE"])
@require_auth
def delete_group_member(gid):
    appid = request.appid

    #群组管理员有权限删除群成员
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
@require_auth
def group_member_setting(gid, memberid):
    appid = request.appid
    uid = request.uid

    if uid != memberid:
        raise ResponseMeta(400, "setting other is forbidden")

    obj = json.loads(request.data)
    if obj.has_key('quiet'):
        User.set_group_do_not_disturb(g.rds, appid, uid, gid, obj['quiet'])
    elif obj.has_key('do_not_disturb'):
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
