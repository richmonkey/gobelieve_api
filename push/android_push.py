# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
from apns import APNs, Payload
import json
import uuid
import subprocess
from OpenSSL import crypto
import os
import traceback
import threading
import socket
import binascii
import mysql
import config
import npush

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB,
                        password=config.REDIS_PASSWORD)

mysql = mysql.Mysql.instance(*config.MYSQL_GC)


class APNSConnectionManager:
    def __init__(self):
        self.apns_connections = {}
        self.lock = threading.Lock()

    def get_apns_connection(self, appid):
        self.lock.acquire()
        try:
            connections = self.apns_connections
            apns = connections[appid] if connections.has_key(appid) else None
        finally:
            self.lock.release()
        return apns

    def remove_apns_connection(self, appid):
        self.lock.acquire()
        try:
            connections = self.apns_connections
            if connections.has_key(apid):
                logging.debug("pop client:%s", appid)
                connections.pop(appid)
        finally:
            self.lock.release()

    def set_apns_connection(self, appid, connection):
        self.lock.acquire()
        try:
            self.apns_connections[appid] = connection
        finally:
            self.lock.release()


class AndroidPush(object):
    apns_manager = APNSConnectionManager()
    app_names = {}

    @staticmethod
    def get_certificate(appid):
        for i in range(2):
            try:
                sql = '''select cc.cer as cer, cc.pkey as pkey
                          from app, client as c, client_certificate as cc where c.app_id=%s and c.id=cc.client_id'''
                cursor = mysql.execute(sql, appid)
                obj = cursor.fetchone()
                cer = obj["cer"]
                key = obj["pkey"]
                return cer, key
            except Exception, e:
                logging.info("exception:%s", str(e))
                continue

        return None, None

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
        return None
        
    @staticmethod
    def connect(appid):
        cer, pkey = AndroidPush.get_certificate(appid)
        if cer is None or pkey is None:
            return None

        cer_file = "/tmp/android_app_%s.cer" % (appid)
        key_file = "/tmp/android_app_%s.key" % (appid)
        f = open(cer_file, "wb")
        f.write(cer)
        f.close()

        f = open(key_file, "wb")
        f.write(pkey)
        f.close()

        npush_conn = npush.Connection(cer_file, key_file)
        return npush_conn

    @classmethod
    def get_connection(cls, appid):
        apns = cls.apns_manager.get_apns_connection(appid)
        if not apns:
            apns = cls.connect(appid)
            if not apns:
                logging.warn("get p12 fail client id:%s", client_id)
                return None
            cls.apns_manager.set_apns_connection(appid, apns)
        return apns

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
        obj = {}
        obj["title"] = cls.get_title(appid)
        obj["push_type"] = 1
        obj["is_ring"] = True
        obj["is_vibrate"] = True
        obj["content"] = content
        obj["app_params"] = {}
         
        for i in range(2):
            if i == 1:
                logging.warn("resend notification")
            try:
                npush_conn = cls.get_connection(appid)
                if npush_conn is None:
                    continue

                notification = npush.EnhancedNotification()
                notification.token = token
                notification.identifier = 1
                notification.expiry = int(time.time()+3600)
                notification.payload = json.dumps(obj)
                logging.debug("ng notification:%s", notification.payload)
                npush_conn.write_notification(notification)
                break
            except Exception, e:
                print_exception_traceback()
                continue

def print_exception_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logging.warn("exception traceback:%s", traceback.format_exc())
