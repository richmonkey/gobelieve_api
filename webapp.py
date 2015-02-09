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

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
authorization.rds = rds


urls = (
  '/', 'index',
  '/qrcode/login', 'QRLogin',
  '/qrcode/sweep', 'QRSweep',
  '/qrcode/(.*)', 'QRCode'
)

app = web.application(urls, globals())

HTTP_STATUS_CODES = {
    100:    'Continue',
    101:    'Switching Protocols',
    102:    'Processing',
    200:    'OK',
    201:    'Created',
    202:    'Accepted',
    203:    'Non Authoritative Information',
    204:    'No Content',
    205:    'Reset Content',
    206:    'Partial Content',
    207:    'Multi Status',
    226:    'IM Used',              # see RFC 3229
    300:    'Multiple Choices',
    301:    'Moved Permanently',
    302:    'Found',
    303:    'See Other',
    304:    'Not Modified',
    305:    'Use Proxy',
    307:    'Temporary Redirect',
    400:    'Bad Request',
    401:    'Unauthorized',
    402:    'Payment Required',     # unused
    403:    'Forbidden',
    404:    'Not Found',
    405:    'Method Not Allowed',
    406:    'Not Acceptable',
    407:    'Proxy Authentication Required',
    408:    'Request Timeout',
    409:    'Conflict',
    410:    'Gone',
    411:    'Length Required',
    412:    'Precondition Failed',
    413:    'Request Entity Too Large',
    414:    'Request URI Too Long',
    415:    'Unsupported Media Type',
    416:    'Requested Range Not Satisfiable',
    417:    'Expectation Failed',
    418:    'I\'m a teapot',        # see RFC 2324
    422:    'Unprocessable Entity',
    423:    'Locked',
    424:    'Failed Dependency',
    426:    'Upgrade Required',
    428:    'Precondition Required', # see RFC 6585
    429:    'Too Many Requests',
    431:    'Request Header Fields Too Large',
    449:    'Retry With',           # proprietary MS extension
    500:    'Internal Server Error',
    501:    'Not Implemented',
    502:    'Bad Gateway',
    503:    'Service Unavailable',
    504:    'Gateway Timeout',
    505:    'HTTP Version Not Supported',
    507:    'Insufficient Storage',
    510:    'Not Extended'
}

class Error(web.HTTPError):
    def __init__(self, status_code,  err):
        data = json.dumps({"error":err})
        headers = {"Content-Type":"application/json"}
        status = "%s %s"%(status_code, HTTP_STATUS_CODES[status_code])
        web.HTTPError.__init__(self, status, headers, data=data)
    

class NotFound(web.HTTPError):
    """`404 Not Found` error."""
    message = "not found"
    def __init__(self, message=None):
        status = '404 Not Found'
        headers = {'Content-Type': 'text/html'}
        web.HTTPError.__init__(self, status, headers, message or self.message)

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
        sid = str(uuid.uuid1())
        session = Session()
        session.sid = sid
        session.uid = ""
        session.save(rds)
        logging.debug("new sid:%s", sid)
        render = web.template.render('templates/')
        return render.index(sid)

def wait_sweep(sid):
    lrds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    key = "session_queue_" + sid
    e = lrds.brpop(key, timeout=3*60)
    return e

def post_sweep_notification(rds, sid):
    key = "session_queue_" + sid
    pipe = rds.pipeline()
    pipe.rpush(key, "e")
    pipe.expire(key, 30*60)
    pipe.execute()

class QRLogin:
    def GET(self):
        logging.debug("qrcode login")
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
            t = token.Token(**tok)
            t.user_id = session.uid
            t.save(rds)
            tok['uid'] = session.uid
            return json.dumps(tok)
         
        e = wait_sweep(sid)
        if not e:
            raise Error(400, "180s timeout")

        session.load(rds)
        if not session.is_valid:
            raise Error(404, "sid not found")
         
        if session.uid:
            #已经登录
            tok = create_token(3600, True)
            t = token.Token(**tok)
            t.user_id = session.uid
            t.save(rds)
            tok['uid'] = session.uid
            return json.dumps(tok)

        logging.warning("session login fail")
        raise Error(400, "180s timeout")


class QRSweep:
    def POST(self):
        data = web.data()
        obj = json.loads(data)
        sid = obj["sid"]
        t = obj["token"]

        tok = token.AccessToken()
        tok.load(rds, t)
        if not tok.user_id:
            raise Error(400, "token is't exist")

        session = Session()
        session.sid = sid
        session.uid = tok.user_id
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
                        format='%(filename)s:%(lineno)d -  %(levelname)s - %(message)s')

log = logging.getLogger('')
init_logger(log)
logging.debug("startup")


application = app.wsgifunc()

if __name__ == "__main__": 
    app.run()      
