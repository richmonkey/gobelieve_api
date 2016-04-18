# -*- coding: utf-8 -*-
from flask import request
from flask import Flask
from flask import g
import flask
import md5
import json
import logging
import sys
import os
import random
import redis

from views import image
from views import audio
from views import message
from views import group
from views import user
from views import notification
from views import application

import config
from views import authorization
from libs.response_meta import ResponseMeta
from libs.mysql import Mysql
from libs.fs import FS


app = Flask(__name__)
app.debug = config.DEBUG

FS.HOST = config.FS_HOST
FS.PORT = config.FS_PORT

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)

authorization.rds = rds
group.rds = rds
user.rds = rds
notification.rds = rds
application.rds = rds

LOGGER = logging.getLogger('')

def before_request():
    LOGGER.debug("before request")
    cnf = config.MYSQL
    imcnf = config.MYSQL_IM
    db = getattr(g, '_db', None)    
    if db is None:
        g._db = Mysql(*cnf)

    imdb = getattr(g, '_imdb', None)
    if imdb is None:
        g._imdb = Mysql(*imcnf)

def app_teardown(exception):
    LOGGER.debug('app_teardown')
    # 捕获teardown时的mysql异常
    try:
        db = getattr(g, '_db', None)
        if db:
            db.close()
        imdb = getattr(g, '_imdb', None)
        if imdb:
            imdb.close()

        mysql_instances = getattr(g, '_mysql_instances', None)
        if mysql_instances is not None:
            for mysql in mysql_instances.values():
                mysql.close()
    except Exception:
        pass


def http_error_handler(err):
    LOGGER.error(err)
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

    app.register_blueprint(image.app)
    app.register_blueprint(audio.app)
    app.register_blueprint(message.app)
    app.register_blueprint(group.app)
    app.register_blueprint(user.app)
    app.register_blueprint(notification.app)
    app.register_blueprint(application.app)

random.seed()

log = logging.getLogger('')
init_logger(log)

init_app(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
