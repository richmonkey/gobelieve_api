# -*- coding: utf-8 -*-
import time


class User(object):
    @staticmethod
    def get_user_access_token(rds, appid, uid):
        key = "users_%d_%d"%(appid, uid)
        token = rds.hget(key, "access_token")
        return token

    @staticmethod
    def load_user_access_token(rds, token):
        key = "access_token_%s"%token
        exists = rds.exists(key)
        if not exists:
            return 0, 0, ""
        uid, appid, name = rds.hget(key, "user_id", "app_id", "user_name")
        return uid, appid, name

    @staticmethod
    def save_user_access_token(rds, appid, uid, name, token):
        pipe = rds.pipeline()

        key = "access_token_%s"%token
        obj = {
            "user_id":uid,
            "user_name":name,
            "app_id":appid
        }
        
        pipe.hmset(key, obj)

        key = "users_%d_%d"%(appid, uid)
        obj = {
            "access_token":token,
            "name":name
        }

        pipe.hmset(key, obj)
        pipe.execute()

        return True

    @staticmethod
    def save_user_device_token(rds, appid, uid, device_token, 
                               ng_device_token, xg_device_token,
                               xm_device_token, hw_device_token,
                               gcm_device_token):
        now = int(time.time())
        key = "users_%d_%d"%(appid, uid)

        if device_token:
            obj = {
                "apns_device_token":device_token,
                "apns_timestamp":now
            }
            rds.hmset(key, obj)
            
        if ng_device_token:
            obj = {
                "ng_device_token":ng_device_token,
                "ng_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xg_device_token:
            obj = {
                "xg_device_token":xg_device_token,
                "xg_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xm_device_token:
            obj = {
                "xm_device_token":xm_device_token,
                "xm_timestamp":now
            }
            rds.hmset(key, obj)

        if hw_device_token:
            obj = {
                "hw_device_token":hw_device_token,
                "hw_timestamp":now
            }
            rds.hmset(key, obj)
        
        if gcm_device_token:
            obj = {
                "gcm_device_token":gcm_device_token,
                "gcm_timestamp":now
            }
            rds.hmset(key, obj)
            
        return True


    #重置(清空)用户已经绑定的devicetoken
    @staticmethod
    def reset_user_device_token(rds, appid, uid, device_token, 
                                ng_device_token, xg_device_token, 
                                xm_device_token, hw_device_token, 
                                gcm_device_token):
        key = "users_%d_%d"%(appid, uid)
        if device_token:
            t = rds.hget(key, "apns_device_token")
            if device_token == t:
                return False
            rds.hdel(key, "apns_device_token")

        if ng_device_token:
            t = rds.hget(key, "ng_device_token")
            if ng_device_token == t:
                return False
            rds.hdel(key, "ng_device_token")
            
        if xg_device_token:
            t = rds.hget(key, "xg_device_token")
            if xg_device_token == t:
                return False
            rds.hdel(key, "xg_device_token")

        if xm_device_token:
            t = rds.hget(key, "xm_device_token")
            if xm_device_token == t:
                return False
            rds.hdel(key, "xm_device_token")

        if hw_device_token:
            t = rds.hget(key, "hw_device_token")
            if hw_device_token == t:
                return False
            rds.hdel(key, "hw_device_token")

        if gcm_device_token:
            t = rds.hget(key, "gcm_device_token")
            if gcm_device_token == t:
                return False
            rds.hdel(key, "gcm_device_token")
        
        return True

    @staticmethod
    def set_user_name(rds, appid, uid, name):
        key = "users_%d_%d"%(appid, uid)
        rds.hset(key, "name", name)

    @staticmethod
    def add_user_count(rds, appid, uid):
        pass
