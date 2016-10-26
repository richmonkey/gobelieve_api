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
from authorization import require_application_or_person_auth
from authorization import require_application_auth
from authorization import require_auth
from authorization import require_client_auth
from models.user import User
from models.app import App
from models.customer import Customer
from models.seller import Seller
from models.supporter import Supporter
from rpc import init_message_queue
from libs.util import make_json_response

app = Blueprint('supporter', __name__)


#获取一个客服id
@app.route("/supporters", methods=["GET"])
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
    
    online_sellers = []
    sellers = Seller.get_sellers(db, store_id)

    if not sellers:
        raise ResponseMeta(400, 'store no supporter')

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

    name = ""
    if seller.has_key('name') and seller['name']:
        name = seller['name'].split('@')[0]

    resp = {
        "seller_id":seller['id'], 
        "name":name,
        "status":seller["status"]
    }
    return make_json_response({"data":resp} , 200)
    
    
