# -*- coding: utf-8 -*-
import config
import requests
from urllib.parse import urlencode
from flask import request, Blueprint, g
import flask
import logging
import json
from libs.crossdomain import crossdomain
from .authorization import require_application_auth
from .authorization import require_auth
from .authorization import require_application_or_person_auth
from libs.response_meta import ResponseMeta
from libs.util import make_response

from models.customer import Customer
from . import rpc

app = Blueprint('message', __name__)

im_url = config.IM_RPC_URL

    
#发送群组消息
@app.route('/messages/groups', methods=['POST'])
@require_application_auth
def post_group_message():
    appid = request.appid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    res = rpc.post_group_message(appid, obj["sender"], obj["receiver"], obj["content"])
    if res.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(res.content, res.status_code)


#发送个人消息
@app.route('/messages/peers', methods=['POST'])
@require_application_auth
def post_peer_messages():
    appid = request.appid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    resp = rpc.post_peer_message(appid, obj["sender"], obj["receiver"], obj["content"])
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)

#发送通知
@app.route('/messages/notifications', methods=['POST'])
@require_application_auth
def post_notification():
    appid = request.appid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")
    
    uid = obj["receiver"]
    content = obj["content"]
    resp = rpc.post_peer_notification(appid, uid, content)
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)

    
#发送系统消息
@app.route('/messages/systems', methods=['POST'])
@require_application_auth
def post_system_message():
    appid = request.appid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    uid = obj["receiver"]
    content = obj["content"]
    resp = rpc.post_system_message(appid, uid, content)
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)
    

#发送聊天室消息
@app.route('/messages/rooms', methods=['POST'])
@require_application_auth
def post_room_message():
    appid = request.appid
    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    sender = obj["sender"]
    receiver = obj["receiver"]
    content = obj["content"]
    
    resp = rpc.post_room_message(appid, sender, receiver, content)
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)

#发送群通知消息
@app.route('/messages/groups/notifications', methods=['POST'])
@require_application_auth
def post_group_notification():
    appid = request.appid

    obj = request.get_json(force=True, silent=True, cache=False)
    if obj is None:
        logging.debug("json decode err:%s", e)
        raise ResponseMeta(400, "json decode error")

    group_id = obj["group_id"]
    content = obj["content"]
    resp = rpc.post_group_notification_s(appid, group_id, content, [])
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)



MSG_CUSTOMER = 24;
MSG_CUSTOMER_SUPPORT = 25;

@app.route('/messages', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers=['Authorization'])
@require_auth
def get_history_message():
    appid = request.appid
    uid = request.uid
    limit = 1024
    params = {
        "appid": appid,
        "uid": uid,
        "limit":limit
    }
    
    store_id = request.args.get('store')
    if store_id:
        store_id = int(store_id)
    url = im_url + "/load_latest_message?" + urlencode(params)
    resp = requests.get(url)

    if store_id and resp.status_code == 200:
        logging.debug("filter message store id:%s", store_id)
        r = json.loads(resp.content)
        msgs = r['data']
        f = lambda m:(m['command'] == MSG_CUSTOMER or m['command'] == MSG_CUSTOMER_SUPPORT) and m['store_id'] == store_id
        data = [m for m in msgs if f(m)]
        return flask.make_response(json.dumps({"data":data}), 200)
    else:
        response = flask.make_response(resp.content, resp.status_code)
        return response

@app.route('/messages/dequeue', methods=['POST'])
@crossdomain(origin='*', headers=['Authorization'])
@require_auth
def dequeue_message():
    appid = request.appid
    uid = request.uid
    return make_response(200, {"data":{"success":True}})

@app.route('/messages/offline', methods=['GET'])
@require_application_or_person_auth
def get_offline_message():
    rds = g.rds
    appid = request.appid
    customer_id = request.args.get("customer_id", "")
    uid = int(request.args.get("uid", 0))
    if not uid and  hasattr(request, 'uid'):
        uid = request.uid

    if not uid and customer_id:
        uid = Customer.get_client_id(rds, appid, customer_id)

    if not uid:
        raise ResponseMeta(400, "invalid uid")

    platform_id = int(request.args.get("platform_id", 0))
    device_id = request.args.get("device_id", "")

    params = {
        "appid": appid,
        "uid": uid,
        "device_id":device_id,
        "platform_id":platform_id,
    }

    #获取离线消息数目
    count = rpc.get_offline_count(appid, uid, platform_id, device_id)
    new = 1 if count > 0 else 0
    data = {"data":{"count":count, "new":new}}
    return make_response(200, data)

