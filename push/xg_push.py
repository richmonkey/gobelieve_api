# -*- coding: utf-8 -*-

import requests
import time
import json
import hashlib
import logging
import mysql
import config

XINGE_API = "http://openapi.xg.qq.com"
HTTP_METHOD = "POST"
XINGE_HOST = "openapi.xg.qq.com"

mysql = mysql.Mysql.instance(*config.MYSQL_GC)


def GenSign(path, params, secretKey):
    ks = sorted(params.keys())
    paramStr = ''.join([('%s=%s' % (k, params[k])) for k in ks])
    signSource = u'%s%s%s%s%s' % (HTTP_METHOD, XINGE_HOST, path, paramStr, secretKey)
    return hashlib.md5(signSource).hexdigest()

class XGPush:
    xg_apps = {}
    app_names = {}

    @classmethod
    def get_xg_secret(cls, appid):
        for i in range(2):
            try:
                sql = '''select cc.xinge_access_id as access_id, cc.xinge_secret_key as secret_key
                          from client as c, client_certificate as cc where c.app_id=%s and c.id=cc.client_id'''
                cursor = mysql.execute(sql, appid)
                obj = cursor.fetchone()
                access_id = obj["access_id"]
                secret_key = obj["secret_key"]
                return access_id, secret_key
            except Exception, e:
                logging.info("exception:%s", str(e))
                continue

        return None, None

    @classmethod
    def get_xg_app(cls, appid):
        now = int(time.time())
        app = cls.xg_apps[appid] if cls.xg_apps.has_key(appid) else None
        #app不在缓存中或者缓存超时,从数据库获取最新的accessid和secretkey
        if app is None or now - app["timestamp"] > 60:
            access_id, secret_key = XGPush.get_xg_secret(appid)
            if access_id is None or secret_key is None:
                return None
            app = {}
            app["timestamp"] = now
            app["access_id"] = access_id
            app["secret_key"] = secret_key
            app["appid"] = appid
            cls.xg_apps[appid] = app
        return app

    @staticmethod
    def get_app_name(appid):
        for i in range(2):
            try:
                sql = "select name from app where id=%s"
                cursor = mysql.execute(sql, appid)
                obj = cursor.fetchone()
                return obj["name"]
            except Exception, e:
                logging.info("exception:%s", str(e))
                continue
        return ""

    @classmethod
    def get_title(cls, appid):
        if not cls.app_names.has_key(appid):
            name = cls.get_app_name(appid)
            if name is not None:
                cls.app_names[appid] = name

        if cls.app_names.has_key(appid):
            return cls.app_names[appid]
        else:
            return ""

    @classmethod
    def push(cls, appid, token, content):
        #content = content.encode("utf-8")
        #content = "123"
        path = "/v2/push/single_device"
        url = XINGE_API + path

        obj =  {}
        obj["title"] = cls.get_title(appid)
        obj["content"] = content
        obj["vibrate"] = 1

        app = XGPush.get_xg_app(appid)
        if app is None:
            logging.warning("can't read xinge access id")
            return False

        msg = json.dumps(obj, separators=(',',':'))

        params = {
            "access_id":app["access_id"],
            "timestamp":int(time.time()), 
            "expire_time":3600*24,
            "device_token":token,
            "message_type":1,
            "message":msg
        }
         
        params["sign"] = GenSign(path, params, app["secret_key"])
        headers = {"content-type":"application/x-www-form-urlencoded"}
         
        r = requests.post(url, headers=headers, data=params)
        return r.status_code == 200
