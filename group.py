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
from authorization import require_application_or_person_auth

from util import make_response

app = Blueprint('group', __name__)

im_url=config.IM_RPC_URL

rds = None

def publish_message(channel, msg):
    rds.publish(channel, msg)

def send_group_notification(appid, gid, op, members):
    url = im_url + "/post_group_notification"

    obj = {
        "appid": appid,
        "group_id": gid,
        "notification":json.dumps(op)
    }
    if members:
        obj["members"] = members

    headers = {"Content-Type":"application/json"}

    data = json.dumps(obj)
    resp = requests.post(url, data=data, headers=headers)
    if resp.status_code != 200:
        logging.warning("send group notification error:%s", resp.content)
    else:
        logging.debug("send group notification success:%s", data)

class Group(object):
    @staticmethod
    def create_group(db, appid, master, name, is_super, members):
        db.begin()
        sql = "INSERT INTO `group`(appid, master, name, super) VALUES(%s, %s, %s, %s)"

        s = 1 if is_super else 0
        r = db.execute(sql, (appid, master, name, s))
        group_id = r.lastrowid
        
        for m in members:
            sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
            db.execute(sql, (group_id, m))
        
        db.commit()
        return group_id

    @staticmethod
    def update_group_name(db, group_id, name):
        sql = "UPDATE `group` SET name=%s WHERE id=%s"
        r = db.execute(sql, (name, group_id))
        logging.debug("update group rows:%s", r.rowcount)

    @staticmethod
    def disband_group(db, group_id):
        db.begin()
        sql = "DELETE FROM `group` WHERE id=%s"
        r = db.execute(sql, group_id)
        logging.debug("rows:%s", r.rowcount)

        sql = "DELETE FROM group_member WHERE group_id=%s"
        r = db.execute(sql, group_id)
        logging.debug("delete group rows:%s", r.rowcount)
        db.commit()

    @staticmethod
    def add_group_member(db, group_id, member_id):
        sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("insert rows:%s", r.rowcount)

    @staticmethod
    def delete_group_member(db, group_id, member_id):
        sql = "DELETE FROM group_member WHERE group_id=%s AND uid=%s"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("delete group member rows:%s", r.rowcount)

    @staticmethod
    def get_group_master(db, group_id):
        sql = "SELECT master FROM `group` WHERE id=%s"
        cursor = db.execute(sql, group_id)
        r = cursor.fetchone()
        master = r["master"]
        return master
        
@app.route("/groups", methods=["POST"])
@require_application_or_person_auth
def create_group():
    appid = request.appid
    obj = json.loads(request.data)
    master = obj["master"]
    name = obj["name"]
    is_super = obj["super"] if obj.has_key("super") else False
    members = obj["members"]
    gid = Group.create_group(g._imdb, appid, master, name, is_super, members)
    
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
    return ""

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
    member_id = obj["uid"]
    Group.add_group_member(g._imdb, gid, member_id)

    v = {
        "group_id":gid,
        "member_id":member_id,
        "timestamp":int(time.time())
    }
    op = {"add_member":v}
    send_group_notification(appid, gid, op, [member_id])

    content = "%d,%d"%(gid, member_id)
    publish_message("group_member_add", content)

    return ""

@app.route("/groups/<int:gid>/members/<int:memberid>", methods=["DELETE"])
@require_application_or_person_auth
def delete_group_member(gid, memberid):
    appid = request.appid
    if request.uid > 0:
        #群组管理员或者成员本身有权限退出群
        if memberid != request.uid:
            master = Group.get_group_master(g._imdb, gid)
            if master != request.uid:
                raise ResponseMeta(400, "no authority")


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

    return ""

