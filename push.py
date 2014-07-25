import time
import logging
import sys
import redis
from apns import APNs, Frame, Payload
from model import user
import json
import config

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)

apns = APNs(use_sandbox=config.USE_SANDBOX, cert_file=config.CERT_FILE, key_file=config.KEY_FILE)

def main():
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
        payload = Payload(alert=obj["content"], sound="default", badge=1)
        apns.gateway_server.send_notification(token, payload)

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
