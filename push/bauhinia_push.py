# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
import json
import config
import traceback
import binascii

from ios_push import IOSPush
from android_push import AndroidPush

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


class User:
    def __init__(self):
        self.apns_device_token = None
        self.ng_device_token = None
        self.uid = None
        self.appid = None
        self.name = ""

def get_user(rds, appid, uid):
    u = User()
    key = "users_%s_%s"%(appid, uid)
    u.apns_device_token, u.ng_device_token = rds.hmget(key, "apns_device_token", "ng_device_token")
    u.appid = appid
    u.uid = uid
    return u

def ios_push(appid, u, body):
    token = u.apns_device_token
    sound = "default"
    badge = 1

    try:
        content = json.loads(body)
        if content.has_key("text"):
            alert = content["text"]
        elif content.has_key("audio"):
            alert = u"收到一条语音"
        elif content.has_key("image"):
            alert = u"收到一张图片"
        else:
            alert = u"收到一条消息"

    except ValueError:
        alert = u"收到一条消息"

    IOSPush.push(appid, token, alert, sound, badge)

def android_push(appid, u, body):
    token = u.ng_device_token
    token = binascii.a2b_hex(token)

    try:
        content = json.loads(body)
        if content.has_key("text"):
            push_content  = content["text"]
        elif content.has_key("audio"):
            push_content = u"你收到一条语音"
        elif content.has_key("image"):
            push_content = u"你收到一张图片"
        else:
            push_content = u"你收到一条消息"
    except ValueError:
        push_content = u"你收到一条消息"

    AndroidPush.push(appid, token, push_content)

def receive_offline_message():
    while True:
        item = rds.blpop("push_queue")
        if not item:
            continue
        _, msg = item
        logging.debug("push msg:%s", msg)
        obj = json.loads(msg)
        appid = obj["appid"]
        u = get_user(rds, appid, obj['receiver'])
        if u is None:
            logging.info("uid:%d nonexist", obj["recieiver"])
            continue

        if u.apns_device_token:
            ios_push(appid, u, obj["content"])
        if u.ng_device_token:
            android_push(appid, u, obj["content"])

        if not u.apns_device_token and not u.ng_device_token:
            logging.info("uid:%d has't device token", obj['receiver'])
            continue

def main():
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
