# -*- coding: utf-8 -*-

from flask import request, Blueprint
import flask
from flask import g
import logging
import json
import time
import random

from libs.crossdomain import crossdomain
from libs.util import make_response
from libs.util import create_access_token
from libs.response_meta import ResponseMeta
from .authorization import require_application_or_person_auth
from .authorization import require_application_auth
from .authorization import require_auth
from .authorization import require_client_auth
from models.user import User
from models.app import App
from models.customer import Customer

app = Blueprint('customer', __name__)

@app.route("/customer/register", methods=["POST"])
@crossdomain(origin='*', headers=['Authorization'])
@require_client_auth
def customer_register():
    rds = g.rds
    db = g._db
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    appid = obj.get("appid", 0)
    uid = obj.get("customer_id", "")
    name = obj.get("name", "")
    avatar = obj.get("avatar", "")

    if not appid:
        raise ResponseMeta(400, "invalid param")
    
    store_id = App.get_store_id(db, appid)
    if not store_id:
        raise ResponseMeta(400, "app do not support customer")

    if not uid:
        client_id = Customer.generate_client_id(rds)
    else:
        client_id = Customer.get_client_id(rds, appid, uid)
        if not client_id:
            client_id = Customer.generate_client_id(rds)
            Customer.set_client_id(rds, appid, uid, client_id)

    token = User.get_user_access_token(rds, appid, client_id)
    if not token:
        token = create_access_token()
        User.add_user_count(rds, appid, client_id)

    User.save_user(rds, appid, client_id, name, avatar, token)
    User.save_token(rds, appid, client_id, token)
        
    resp = {
        "token":token,
        "store_id":store_id,
        "client_id":client_id,
    }
    data = {"data":resp}
    return make_response(200, data)

