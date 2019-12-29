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
from libs.response_meta import ResponseMeta
from .authorization import require_application_or_person_auth
from .authorization import require_application_auth
from .authorization import require_auth
from .authorization import require_client_auth
from models.user import User
from models.app import App
from models.customer import Customer
from models.seller import Seller
from models.supporter import Supporter
from libs.util import make_json_response

app = Blueprint('supporter', __name__)


def get_new_seller(rds, sellers):
    online_sellers = []
    for seller in sellers:
        status = Supporter.get_user_status(rds, seller['id'])
        seller['status'] = status
        if status == Supporter.STATUS_ONLINE:
            online_sellers.append(seller)

    if len(online_sellers) == 0:
        #假设第一个客服是管理员
        seller = sellers[0]
    else:
        index = random.randint(0, len(online_sellers) - 1)
        seller = sellers[index]
    return seller

#获取一个客服id
@app.route("/supporters", methods=["GET", "OPTIONS"])
@crossdomain(origin='*', headers=['Authorization'])
@require_auth
def get_one_supporter():
    rds = g.rds
    db = g._db

    appid = request.appid
    uid = request.uid

    store_id = request.args.get('store_id', 0)
    store_id = int(store_id)

    if not store_id:
        raise ResponseMeta(400, 'require store_id param')

    sellers = Seller.get_sellers(db, store_id)
    if not sellers:
        raise ResponseMeta(400, 'store no supporter')

    seller = None
    #获取上次对话的客服id
    last_store_id, last_seller_id = User.get_seller(rds, appid, uid)
    if store_id == last_store_id and last_seller_id > 0:
        for s in sellers:
            if s['id'] == last_seller_id:
                status = Supporter.get_user_status(rds, s['id'])
                s['status'] = status
                seller = s
                break
                
    if not seller:
        seller = get_new_seller(rds, sellers)
        User.set_seller(rds, appid, uid, store_id, seller['id'])
        
    name = ""
    if 'name' in seller and seller['name']:
        name = seller['name'].split('@')[0]

    resp = {
        "seller_id":seller['id'], 
        "name":name,
        "status":seller["status"]
    }
    return make_json_response({"data":resp} , 200)
    
    
