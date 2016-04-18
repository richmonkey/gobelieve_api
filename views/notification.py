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
from authorization import require_auth


app = Blueprint('notification', __name__)
        
rds = None
   
def set_notification_quiet(appid, uid, gid, quiet):
    key = "users_%d_%d"%(appid, uid)
    field = "group_%d"%gid
    rds.hset(key, field, quiet)
    
@app.route("/notification/groups/<int:gid>", methods=["POST"])
@require_auth
def enable_group_notification(gid):
    appid = request.appid
    uid = request.uid
    
    obj = json.loads(request.data)
    quiet = obj["quiet"]
    
    set_notification_quiet(appid, uid, gid, quiet)
    return ""
