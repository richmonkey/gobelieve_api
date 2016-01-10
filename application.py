# -*- coding: utf-8 -*-
from flask import request, Blueprint
import flask
from flask import g
import json
import umysql
import logging
from response_meta import ResponseMeta
from group_model import Group
from user_model import User
from util import make_response
from authorization import require_application_auth

app = Blueprint('application', __name__)
rds = None


def publish_message(channel, msg):
    rds.publish(channel, msg)

class Application(object):
    @staticmethod
    def get_application_cs_group(db, appid):
        sql = 'SELECT cs_group_id FROM app WHERE id=%s'
        cursor = db.execute(sql, (appid,))
        r = cursor.fetchone()
        return r['cs_group_id']

    @staticmethod
    def set_application_cs_group(db, appid, group_id):
        sql = 'UPDATE app SET cs_group_id=%s WHERE id=%s'
        r = db.execute(sql, (group_id, appid))
        logging.debug("update application cs group rows:%s", r.rowcount)

    @staticmethod
    def set_application_cs_mode(db, appid, mode):
        sql = 'UPDATE app SET cs_mode=%s WHERE id=%s'
        r = db.execute(sql, (mode, appid))
        logging.debug("update application cs mode rows:%s", r.rowcount)

def enable_customer_service(appid):
    group_id = Application.get_application_cs_group(g._db, appid)
    if group_id != 0:
        return
         
    group_id = Group.create_group(g._imdb, appid, 0, "customer_service", False, [])
    Application.set_application_cs_group(g._db, appid, group_id)

    content = "%d,%d,%d"%(group_id, appid, 0)
    publish_message("group_create", content)

    
@app.route("/applications/<int:appid>", methods=['PATCH'])
@require_application_auth
def update_applicaton(appid):
    print request.appid, appid
    if request.appid != appid:
        raise ResponseMeta(400, "invalid appid")
        
    obj= json.loads(request.data)
    if obj.has_key('customer_service'):
        enable_cs = obj['customer_service']
        if not enable_cs:
            raise ResponseMeta(400, "do not support disable customer service")
        
        enable_customer_service(appid)

    if obj.has_key('customer_service_mode'):
        mode = obj['customer_service_mode']
        if mode != 1 and mode != 2 and mode != 3:
            raise ResponseMeta(400, "do not support customer service mode:%s"%mode)
        Application.set_application_cs_mode(g._db, appid, mode)

    return ""

@app.route("/applications/<int:appid>/staffs", methods=['POST'])
@require_application_auth
def add_customer_service_staff(appid):
    if request.appid != appid:
        raise ResponseMeta(400, "invalid appid")

    obj = json.loads(request.data)
    staff_uid = obj['staff_uid']
    staff_name = obj['staff_name']
    group_id = Application.get_application_cs_group(g._db, appid)
    if group_id == 0:
        raise ResponseMeta(400, "application customer service is disabled")
    try:
        Group.add_group_member(g._imdb, group_id, staff_uid)
    except umysql.SQLError, e:
        #1062 duplicate member
        if e[0] != 1062:
            raise

    content = "%d,%d"%(group_id, staff_uid)
    publish_message("group_member_add", content)
    
    User.set_user_name(rds, appid, staff_uid, staff_name)
    obj = {'id':staff_uid}
    return make_response(200, obj)

@app.route("/applications/<int:appid>/staffs/<int:staff_id>", methods=['DELETE'])
@require_application_auth
def remove_customer_service_staff(appid, staff_id):
    if request.appid != appid:
        raise ResponseMeta(400, "invalid appid")

    group_id = Application.get_application_cs_group(g._db, appid)
    if group_id == 0:
        raise ResponseMeta(400, "application customer service is disabled")

    Group.delete_group_member(g._imdb, group_id, staff_id)

    content = "%d,%d"%(group_id, staff_id)
    publish_message("group_member_remove", content)

    return ""
    
