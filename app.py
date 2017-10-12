# -*- coding: utf-8 -*-
from flask import request
from flask import Flask
from flask import g
import flask
import md5
import json
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import random
import redis

from views import message
from views import group
from views import user
from libs.response_meta import ResponseMeta
from libs.mysql import Mysql

import config

app = Flask(__name__)
app.debug = config.DEBUG

rds = redis.StrictRedis(host=config.REDIS_HOST, password=config.REDIS_PASSWORD, port=config.REDIS_PORT, db=config.REDIS_DB)


def before_request():
    logging.debug("before request")
    g.rds= rds

    cnf = config.MYSQL
    db = getattr(g, '_db', None)    
    if db is None:
        g._db = Mysql(*cnf)

def app_teardown(exception):
    logging.debug('app_teardown')
    # 捕获teardown时的mysql异常
    try:
        db = getattr(g, '_db', None)
        if db:
            db.close()
    except Exception:
        pass


def http_error_handler(err):
    logging.error(err)
    return ResponseMeta(code=err.code, http_code=err.code)


def response_meta_handler(response_meta):
    return response_meta.get_response()


def generic_error_handler(err):
    logging.exception(err)
    return ResponseMeta(http_code=500, description='Server Internal Error!')


def init_logger(logger):
    root = logger
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s:%(lineno)d -  %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)    

# 初始化接口
def init_app(app):
    app.teardown_appcontext(app_teardown)
    app.before_request(before_request)

    for error in range(400, 420) + range(500, 506):
        app.error_handler_spec[None][error] = http_error_handler
    app.register_error_handler(ResponseMeta, response_meta_handler)
    app.register_error_handler(Exception, generic_error_handler)


    app.register_blueprint(message.app)
    app.register_blueprint(group.app)
    app.register_blueprint(user.app)


random.seed()

log = logging.getLogger('')
init_logger(log)

init_app(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
