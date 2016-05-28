# -*- coding: utf-8 -*-
import config
import requests
from urllib import urlencode
from flask import request, Blueprint
import flask
import logging
import json
from libs.crossdomain import crossdomain
from authorization import require_application_auth
from authorization import require_auth

app = Blueprint('message', __name__)

im_url=config.IM_RPC_URL

def post_message(appid, sender, receiver, cls, content):
    params = {
        "appid":appid,
        "class":cls,
        "sender":sender
    }

    req_obj = {
        "receiver":receiver,
        "content":content,
    }

    url = im_url + "/post_im_message?" + urlencode(params)
    logging.debug("url:%s", url)
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, data=json.dumps(req_obj), headers=headers)
    return res
    
#发送群组消息
@app.route('/messages/groups', methods=['POST'])
@require_application_auth
def post_group_message():
    appid = request.appid
    obj = json.loads(request.data)
    
    res = post_message(appid, obj["sender"], obj["receiver"], 
                               "group", obj["content"])

    if res.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(res.content, res.status_code)


#发送个人消息
@app.route('/messages/peers', methods=['POST'])
@require_application_auth
def post_peer_messages():
    appid = request.appid
    obj = json.loads(request.data)

    resp = post_message(appid, obj["sender"], obj["receiver"], 
                               "peer", obj["content"])

    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)

#发送系统消息
@app.route('/messages/systems', methods=['POST', 'GET'])
@require_application_auth
def post_system_message():
    appid = request.appid
    obj = json.loads(request.data)
    uid = obj["receiver"]
    content = obj["content"]

    params = {
        "appid":appid,
        "uid":uid
    }
    url = im_url + "/post_system_message?" + urlencode(params)

    headers = {"Content-Type":"text/plain; charset=UTF-8"}
    resp = requests.post(url, data=content.encode("utf8"), headers=headers)
    if resp.status_code == 200:
        return flask.make_response("", 200)
    else:
        return flask.make_response(resp.content, resp.status_code)

#发送系统消息
@app.route('/messages/rooms', methods=['POST'])
@require_application_auth
def post_room_message():
    appid = request.appid
    obj = json.loads(request.data)
    sender = obj["sender"]
    receiver = obj["receiver"]
    content = obj["content"]

    params = {
        "appid":appid,
        "uid":sender,
        "room":receiver
    }
    url = im_url + "/post_room_message?" + urlencode(params)

    headers = {"Content-Type":"text/plain; charset=UTF-8"}
    resp = requests.post(url, data=content.encode("utf8"), headers=headers)
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

