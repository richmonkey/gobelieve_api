
# -*- coding: utf-8 -*-
import time

class Customer(object):
    @staticmethod
    def generate_client_id(rds):
        key = "customer_client_id"
        client_id = rds.incr(key)
        return client_id


    @staticmethod
    def get_client_id(rds, appid, uid):
        key = "customer_users_%s_%s"%(appid, uid)
        value = rds.get(key)
        if value:
            return int(value)
        else:
            return 0

    @staticmethod
    def set_client_id(rds, appid, uid, client_id):
        key = "customer_users_%s_%s"%(appid, uid)
        rds.set(key, client_id)

