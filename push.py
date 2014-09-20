# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
from apns import APNs, Payload
from model import user
import json
import config
import traceback

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def receive_offline_message():
    apns = APNs(use_sandbox=config.USE_SANDBOX, cert_file=config.CERT_FILE)

    while True:
        item = rds.blpop("push_queue")
        if not item:
            continue
        _, msg = item
        obj = json.loads(msg)
        u = user.get_user(rds, obj['receiver'])
        if u is None or u.apns_device_token is None:
            logging.info("uid:%d has't device token", obj['receiver'])
            continue
        token = u.apns_device_token
        content = json.loads(obj["content"])

        if content.has_key("text"):
            payload = Payload(alert=content["text"], sound="default", badge=1)
        elif content.has_key("audio"):
            payload = Payload(alert=u"收到一条语音", sound="default", badge=1)
        elif content.has_key("image"):
            payload = Payload(alert=u"收到一张图片", sound="default", badge=1)
        else:
            payload = Payload(alert=u"收到一条消息", sound="default", badge=1)

        for i in range(2):
            if i == 1:
                logging.warn("resend notification")
            try:
                apns.gateway_server.send_notification(token, payload)
                break
            except Exception, e:
                print_exception_traceback()
                apns = APNs(use_sandbox=config.USE_SANDBOX, cert_file=config.CERT_FILE)


def main():
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
    formatter = logging.Formatter('%(filename)s:%(lineno)d -  %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == "__main__":
    init_logger(logging.getLogger(''))
    main()
