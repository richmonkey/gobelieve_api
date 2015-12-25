# -*- coding: utf-8 -*-
import requests
import json
import logging
import application
import time

#文档地址:http://dev.xiaomi.com/doc/?p=533#d5e824
MI_URL = "https://api.xmpush.xiaomi.com/v2/message/regid"

class MiPush:
    session = requests.session()
    mysql = None
    mi_apps = {}
        
    @classmethod
    def get_app(cls, appid):
        now = int(time.time())
        app = cls.mi_apps[appid] if cls.mi_apps.has_key(appid) else None
        #app不在缓存中或者缓存超时,从数据库获取最新的app_secret
        if app is None or now - app["timestamp"] > 60:
            mi_appid, mi_app_secret = application.get_mi_key(cls.mysql, appid)
            if mi_appid is None or mi_app_secret is None:
                return None
            app = {}
            app["timestamp"] = now
            app["mi_appid"] = mi_appid
            app["mi_app_secret"] = mi_app_secret
            app["appid"] = appid
            cls.mi_apps[appid] = app
        return app

    @classmethod
    def send(cls, mi_app_secret, device_token, title, content):
        obj = {
            "registration_id":device_token,
            'title':title,
            'description':content,
            'pass_through':0,
            'notify_type':-1,
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': 'key=' + mi_app_secret}

        res = cls.session.post(MI_URL, data=obj, headers=headers)
        if res.status_code != 200:
            logging.error("send xiaomi message error")
        else:
            obj = json.loads(res.content)
            if obj.has_key("code") and obj["code"] == 0:
                logging.debug("send xiaomi message success")
            else:
                logging.error("send xiaomi message error:%s", res.content)                
        print res.content
        
    @classmethod
    def push(cls, appid, appname, token, content):
        app = cls.get_app(appid)
        if app is None:
            logging.warning("can't read mi app secret")
            return False

        logging.debug("ssssssssssss")
        mi_app_secret = app["mi_app_secret"]
        cls.send(mi_app_secret, token, appname, content)

    
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    APP_SECRET = "fwNtbK7hRqjMp4X/Tgb6Pg=="
    token = "d//igwEhgBGCI2TG6lWqlOlzU8pu8+C4t+wQ4zMxFYhLO0pHWInlKmKMyW9I3gWgby1Z1vq59TkIQQYeaS43gEzCfwuNRp+OkuHM3JCDA5U="
    MiPush.send(APP_SECRET, token, "test", "测试小米推送")
