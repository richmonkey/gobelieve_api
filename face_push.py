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

def apns_listener(err):
    logging.warn("apns err:%s", err)

def receive_offline_message():
    identifier = 0
    apns = APNs(use_sandbox=config.FACE_USE_SANDBOX, cert_file=config.FACE_CERT_FILE, enhanced=True)
    apns.gateway_server.register_response_listener(apns_listener)
    while True:
        item = rds.blpop("face_push_queue")
        if not item:
            continue
        _, msg = item
        obj = json.loads(msg)
        u = user.get_user(rds, obj['receiver'])
        if u is None or u.face_apns_device_token is None:
            logging.info("uid:%d has't device token", obj['receiver'])
            continue
        token = u.face_apns_device_token
        content = obj["content"]
        logging.info("sender:%d receiver:%d token:%s content:%s", 
                     obj["sender"], obj["receiver"], token, content)
        payload = Payload(alert=content, sound="default", badge=1)
        identifier += 1
        for i in range(2):
            if i == 1:
                logging.warn("resend notification")
            try:
                apns.gateway_server.send_notification(token, payload, identifier=identifier)
                break
            except Exception, e:
                print_exception_traceback()

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
