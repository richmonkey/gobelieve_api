# -*- coding: utf-8 -*-
import time


class Supporter(object):
    STATUS_ONLINE = "online"
    STATUS_OFFLINE = "offline"
    
    @staticmethod
    def set_user_online(rds, uid):
        key = "supporters_%d"%uid
        rds.hset("status", "online")

    @staticmethod
    def set_user_offline(rds, uid):
        key = "supporters_%d"%uid
        rds.hset("status", "offline")

    @staticmethod
    def get_user_status(rds, uid):
        key = "supporters_%d"%uid
        status = rds.hget(key, "status")
        if not status:
            status = Supporter.STATUS_OFFLINE
        return status
