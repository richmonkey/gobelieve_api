# -*- coding: utf-8 -*-

import qrcode
from gevent import monkey
monkey.patch_socket()
import web
import json
import redis
import authorization
from authorization import create_token
from model import token
import config
import logging
import sys
from error import Error


TOKEN_EXPIRE = 3600*12

urls = (
  '/qrcode/login', 'QRLogin',
)

app = web.application(urls, globals())

class Session:
    def __init__(self):
        self.sid = None
        self.uid = None
        self.is_valid = False

    def save(self, rds):
        key = "session_" + self.sid
        pipe = rds.pipeline()
        pipe.set(key, self.uid)
        pipe.expire(key, 30*60)
        pipe.execute()

    def load(self, rds):
        key = "session_" + self.sid
        self.is_valid = rds.exists(key)
        if self.is_valid:
            self.uid = rds.get(key)
    def expire(self, rds, time):
        key = "session_" + self.sid
        rds.expire(key, time)
        

def wait_sweep(sid):
    key = "session_queue_" + sid
    rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    e = rds.brpop(key, timeout=55)
    return e

class QRLogin:
    def GET(self):
        logging.debug("qrcode login")
        rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        sid = web.input().sid
        session = Session()
        session.sid = sid
        session.load(rds)
         
        if not session.is_valid:
            logging.debug("sid not found")
            raise Error(404, "sid not found")
         
        if session.uid:
            #已经登录
            tok = create_token(3600, True)
            tok['uid'] = int(session.uid)
            t = token.AccessToken(**tok)
            t.save(rds)

            session.expire(rds, TOKEN_EXPIRE)

            web.setcookie("sid", sid, TOKEN_EXPIRE)
            web.setcookie("token", t.access_token, TOKEN_EXPIRE)
            return json.dumps(tok)
         
        e = wait_sweep(sid)
        if not e:
            logging.debug("qrcode login timeout")
            raise Error(400, "timeout")

        session.load(rds)
        if not session.is_valid:
            raise Error(404, "sid not found")
         
        if session.uid:
            #已经登录
            tok = create_token(3600, True)
            tok['uid'] = int(session.uid)
            t = token.AccessToken(**tok)
            t.save(rds)

            session.expire(rds, TOKEN_EXPIRE)

            web.setcookie("sid", sid, TOKEN_EXPIRE)
            web.setcookie("token", t.access_token, TOKEN_EXPIRE)
            return json.dumps(tok)

        logging.warning("session login fail")
        raise Error(400, "timeout")


def init_logger(logger):
    root = logger
    root.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(filename)s:%(lineno)d- %(asctime)s-%(levelname)s - %(message)s')

log = logging.getLogger('')
init_logger(log)
logging.debug("startup")


application = app.wsgifunc()

if __name__ == "__main__": 
    app.run()      
