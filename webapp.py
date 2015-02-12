# -*- coding: utf-8 -*-

import qrcode
import web
from qrcode.image.pil import PilImage
import StringIO
import uuid
import json
import redis
import authorization
from authorization import create_token
from model import token
import config
import logging
import sys
from error import Error
from authorization import web_requires_auth

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
authorization.rds = rds


urls = (
  '/', 'index',
  '/index.html', 'index',
  '/qrcode/session', 'QRSession',
  '/qrcode/sweep', 'QRSweep',
  '/qrcode/(.*)', 'QRCode'
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
        

class index:
    def GET(self):
        sid = web.cookies().get("sid")
        if not sid:
            sid = str(uuid.uuid1())
            session = Session()
            session.sid = sid
            session.uid = ""
            session.save(rds)
            logging.debug("new sid:%s", sid)
        else:
            logging.debug("sid:%s", sid)
        render = web.template.render('templates/')
        return render.index(sid)

#for test
class QRSession:
    def GET(self):
        sid = str(uuid.uuid1())
        session = Session()
        session.sid = sid
        session.uid = ""
        session.save(rds)
        logging.debug("new sid:%s", sid)
        return json.dumps({"sid":sid})

def post_sweep_notification(rds, sid):
    key = "session_queue_" + sid
    pipe = rds.pipeline()
    pipe.rpush(key, "e")
    pipe.expire(key, 30*60)
    pipe.execute()


@web_requires_auth
class QRSweep:
    def POST(self):
        data = web.data()
        obj = json.loads(data)
        sid = obj["sid"]
        uid = web.ctx.uid
        session = Session()
        session.sid = sid
        session.uid = uid
        session.save(rds)
        post_sweep_notification(rds, sid)
        return

class QRCode:
    def GET(self, id):
        logging.debug("qrcode id:%s", id)
        qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
    
        qr.add_data(id)
        qr.make(fit=True)
        img = qr.make_image(factory=PilImage)
        output = StringIO.StringIO()
        img.save(output)
        return output.getvalue()


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
