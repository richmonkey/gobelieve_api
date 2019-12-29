# -*- coding: utf-8 -*-

import requests

class FS(object):
    HOST = None
    PORT = None
    @classmethod
    def upload(self, path, data):
        url = "http://%s:%d/upload%s"%(self.HOST, self.PORT, path)
        resp = requests.post(url, data)
        return resp.status_code == 200

    @classmethod
    def download(self, path):
        url = "http://%s:%d%s"%(self.HOST, self.PORT, path)
        resp = requests.get(url)
        return resp.content if resp.status_code == 200 else ""



import os

class FS2(object):
    ROOT = None
    @classmethod
    def upload(cls, path, data):
        p = os.path.realpath(cls.ROOT + path)
        with open(p, "wb") as f:
            f.write(data)
            return True
            
    @classmethod
    def download(cls, path):
        p = os.path.realpath(cls.ROOT + path)        
        data = None
        try:
            with open(p, "rb") as f:
                data = f.read()
        except Exception as e:
            pass
        return data
    
