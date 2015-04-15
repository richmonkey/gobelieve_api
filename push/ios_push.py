# -*- coding: utf-8 -*-
import time
import logging
import sys
import redis
from apnsclient import Message, APNs, Session
import json
import uuid
import subprocess
from OpenSSL import crypto
import os
import traceback
import threading

import config
from mysql import Mysql


mysql = Mysql.instance(*config.MYSQL_GC)

sandbox = config.SANDBOX

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
            if connections.has_key(appid):
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


class IOSPush(object):
    apns_manager = APNSConnectionManager()

    @staticmethod
    def get_p12(appid):
        for i in range(2):
            try:
                sql = '''select sandbox_key, sandbox_key_secret, sandbox_key_utime,
                          production_key, production_key_secret, production_key_utime
                          from client_apns, client where client.app_id=%s and client.id=client_apns.client_id'''
                cursor = mysql.execute(sql, appid)
                obj = cursor.fetchone()
                if sandbox:
                    p12 = obj["sandbox_key"]
                    secret = obj["sandbox_key_secret"]
                    timestamp = obj["sandbox_key_utime"]
                else:
                    p12 = obj["production_key"]
                    secret = obj["production_key_secret"]
                    timestamp = obj["production_key_utime"]

                return p12, secret, timestamp
            except Exception, e:
                logging.info("exception:%s", str(e))
                continue

        return None, None, None

    @staticmethod
    def gen_pem(p12, secret):
        p12 = crypto.load_pkcs12(p12, str(secret))
        priv_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
        pub_key = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
        return priv_key + pub_key

    @classmethod
    def connect_apns(cls, appid):
        logging.debug("connecting apns")
        p12, secret, timestamp = cls.get_p12(appid)
        if not p12:
            return None

        if sandbox:
            pem_file = "/tmp/app_%s_sandbox_%s.pem" % (appid, timestamp)
            address = 'push_sandbox'
        else:
            pem_file = "/tmp/app_%s_%s.pem" % (appid, timestamp)
            address = 'push_production'

        if not os.path.isfile(pem_file):
            pem = cls.gen_pem(p12, secret)
            f = open(pem_file, "wb")
            f.write(pem)
            f.close()

        session = Session(read_tail_timeout=1)

        conn = session.get_connection(address, cert_file=pem_file)
        apns = APNs(conn)
        return apns

    @classmethod
    def get_connection(cls, appid):
        apns = cls.apns_manager.get_apns_connection(appid)
        if not apns:
            apns = cls.connect_apns(appid)
            if not apns:
                logging.warn("get p12 fail client id:%s", appid)
                return None
            cls.apns_manager.set_apns_connection(appid, apns)
        return apns

    @classmethod
    def push(cls, appid, token, alert, sound="default", badge=0):
        message = Message([token], alert=alert, badge=badge, sound=sound, extra=None)

        for i in range(100):
            if i > 0:
                logging.warn("resend notification")

            apns = cls.get_connection(appid)
             
            try:
                logging.debug("send apns:%s", message.tokens)
                result = apns.send(message)
             
                for token, (reason, explanation) in result.failed.items():
                    # stop using that token
                    logging.error("failed token:%s", token)
             
                for reason, explanation in result.errors:
                    # handle generic errors
                    logging.error("send notification fail: reason = %s, explanation = %s", reason, explanation)
             
                if result.needs_retry():
                    # extract failed tokens as new message
                    message = result.retry()
                    # re-schedule task with the new message after some delay
                    continue
                else:
                    break
            except Exception, e:
                logging.warn("send notification exception:%s", str(e))
                cls.apns_manager.remove_apns_connection(appid)


    @classmethod
    def receive_p12_update_message(cls):
        chan_rds = redis.StrictRedis(host=config.CHAN_REDIS_HOST, 
                                     port=config.CHAN_REDIS_PORT, 
                                     db=config.CHAN_REDIS_DB,
                                     password=config.CHAN_REDIS_PASSWORD)
        sub = chan_rds.pubsub()
        sub.subscribe("apns_update_p12_channel")
        for msg in sub.listen():
            if msg['type'] == 'message':
                data = msg['data']
                try:
                    appid = int(data)
                except:
                    logging.warn("invalid app id:%s", data)
                    continue
                logging.info("update app:%s p12", appid)
                cls.apns_manager.remove_apns_connection(appid)

    @classmethod
    def update_p12_thread(cls):
        while True:
            try:
                cls.receive_p12_update_message()
            except Exception, e:
                logging.exception(e)

    @classmethod
    def start(cls):
        t = threading.Thread(target=cls.update_p12_thread, args=())
        t.setDaemon(True)
        t.start()
