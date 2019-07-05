# -*- coding: utf-8 -*-
import config
import requests
from urllib.parse import urlencode
from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
from .authorization import require_auth
from models.user import User

app = Blueprint('notification', __name__)
        
@app.route("/notification/groups/<int:gid>", methods=["POST"])
@require_auth
def enable_group_notification(gid):
    appid = request.appid
    uid = request.uid
    
    obj = json.loads(request.data)
    quiet = obj["quiet"]
    User.set_group_notification_quiet(g.rds, appid, uid, quiet)
    return ""
