# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
import json
import config
import traceback
import binascii

import mysql
from ios_push import IOSPush
from android_push import SmartPush
from xg_push import XGPush
from huawei import HuaWeiPush
from gcm import GCMPush
from mipush import MiPush

import application
import user

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
mysql_db = mysql.Mysql.instance(*config.MYSQL)

IOSPush.mysql = mysql_db
SmartPush.mysql = mysql_db
XGPush.mysql = mysql_db
HuaWeiPush.mysql = mysql_db
GCMPush.mysql = mysql_db
MiPush.mysql = mysql_db

app_names = {}

def get_title(appid):
    if not app_names.has_key(appid):
        name = application.get_app_name(mysql_db, appid)
        if name is not None:
            app_names[appid] = name

    if app_names.has_key(appid):
        return app_names[appid]
    else:
        return ""

def push_content(sender_name, body):
    if not sender_name:
        try:
            content = json.loads(body)
            if content.has_key("text"):
                alert = content["text"]
            elif content.has_key("audio"):
                alert = u"你收到了一条消息"
            elif content.has_key("image"):
                alert = u"你收到了一张图片"
            else:
                alert = u"你收到了一条消息"
         
        except ValueError:
            alert = u"你收到了一条消息"

    else:
        try:
            sender_name = sender_name.decode("utf8")
            content = json.loads(body)
            if content.has_key("text"):
                alert = "%s:%s"%(sender_name, content["text"])
            elif content.has_key("audio"):
                alert = "%s%s"%(sender_name, u"发来一条语音消息")
            elif content.has_key("image"):
                alert = "%s%s"%(sender_name, u"发来一张图片")
            else:
                alert = "%s%s"%(sender_name, u"发来一条消息")
         
        except ValueError:
            alert = "%s%s"%(sender_name, u"发来一条消息")
    return alert

def ios_push(appid, token, content, badge, extra):
    sound = "default"
    alert = content
    IOSPush.push(appid, token, alert, sound, badge, extra)

def android_push(appid, appname, token, content, extra):
    token = binascii.a2b_hex(token)
    SmartPush.push(appid, appname, token, content, extra)

def xg_push(appid, appname, token, content, extra):
    XGPush.push(appid, appname, token, content, extra)
    
def receive_offline_message():
    while True:
        item = rds.blpop("push_queue")
        if not item:
            continue
        _, msg = item
        obj = json.loads(msg)
        if not obj.has_key("appid") or not obj.has_key("sender") or \
           (not obj.has_key("receiver") and not obj.has_key("receivers")):
            logging.warning("invalid push msg:%s", msg)
            continue

        logging.debug("push msg:%s", msg)

        appid = obj["appid"]
        sender = obj["sender"]

        receivers = []
        if obj.has_key("receiver"):
            receivers = [obj["receiver"]]
        elif obj.has_key("receivers"):
            receivers = obj["receivers"]
            
        group_id = obj["group_id"] if obj.has_key("group_id") else 0

        appname = get_title(appid)
        sender_name = user.get_user_name(rds, appid, sender)

        content = push_content(sender_name, obj["content"])

        extra = {}
        extra["sender"] = sender
        
        if group_id:
            extra["group_id"] = group_id

        for receiver in receivers:
            u = user.get_user(rds, appid, receiver)
            if u is None:
                logging.info("uid:%d nonexist", receiver)
                continue
             
            #找出最近绑定的token
            ts = max(u.apns_timestamp, u.xg_timestamp, u.ng_timestamp, u.mi_timestamp, u.hw_timestamp, u.gcm_timestamp)

            if u.apns_device_token and u.apns_timestamp == ts:
                ios_push(appid, u.apns_device_token, content, u.unread + 1, extra)
                user.set_user_unread(rds, appid, receiver, u.unread+1)
            elif u.ng_device_token and u.ng_timestamp == ts:
                android_push(appid, appname, u.ng_device_token, content, extra)
            elif u.xg_device_token and u.xg_timestamp == ts:
                xg_push(appid, appname, u.xg_device_token, content, extra)
            elif u.mi_device_token and u.mi_timestamp == ts:
                MiPush.push(appid, appname, u.mi_device_token, content)
            elif u.hw_device_token and u.hw_timestamp == ts:
                HuaWeiPush.push(appid, appname, u.hw_device_token, content)
            elif u.gcm_device_token and u.gcm_timestamp == ts:
                GCMPush.push(appid, appname, u.gcm_device_token, content)
            else:
                logging.info("uid:%d has't device token", receiver)
                continue

def main():
    logging.debug("startup")
    IOSPush.start()
    while True:
        try:
            receive_offline_message()
        except Exception, e:
            print_exception_traceback()
            time.sleep(1)
            continue

def print_exception_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logging.warn("exception traceback:%s", traceback.format_exc())

def init_logger(logger):
    root = logger
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d -  %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == "__main__":
    init_logger(logging.getLogger(''))
    main()
