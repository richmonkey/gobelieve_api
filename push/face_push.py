# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
import json
import traceback
import binascii
import config
import mysql
from ios_push import IOSPush
import user

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
mysql = mysql.Mysql.instance(*config.MYSQL)

IOSPush.mysql = mysql

def ios_push(appid, u, content):
    token = u.apns_device_token
    sound = "apns.caf"
    badge = 0

    IOSPush.push(appid, token, content, sound, badge)

def receive_offline_message():
    while True:
        item = rds.blpop("voip_push_queue")
        if not item:
            continue
        _, msg = item
        logging.debug("push msg:%s", msg)
        obj = json.loads(msg)
        appid = obj["appid"]
        u = user.get_user(rds, appid, obj['receiver'])
        if u is None:
            logging.info("uid:%d nonexist", obj["recieiver"])
            continue

        if u.apns_device_token:
            ios_push(appid, u, u"您的朋友请求与您通话")

        if not u.apns_device_token:
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
