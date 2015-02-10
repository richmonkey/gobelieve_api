import time
import logging

def access_token_key(token):
    return "access_token_" + token

def refresh_token_key(token):
    return "refresh_token_" + token


class AccessToken(object):
    def __init__(self, **kwargs):
        if kwargs.has_key('expires_in'):
            expires_in = kwargs.pop('expires_in')
            self.expires = int(time.time()) + expires_in

        if kwargs.has_key('uid'):
            self.user_id = kwargs.pop('uid')
        for k, v in kwargs.items():
            setattr(self, k, v)


    def _save(self, rds, key):
        logging.debug("save key:%s", key)
        pipe = rds.pipeline()
        expires = self.expires
        m = {
            "expires":expires,
            "token_type":self.token_type,
            "user_id":self.user_id,
        }
        pipe.hmset(key, m)
        if expires:
            pipe.expireat(key, expires)
        pipe.execute()


    def _load(self, rds, key):
        t = rds.hmget(key, "expires", "token_type", "user_id")
        self.expires, self.token_type, self.user_id = t
        return True if self.user_id else False

    def load(self, rds, token):
        key = access_token_key(token)
        self.access_token = token
        return self._load(rds, key)

    def save(self, rds):
        key = access_token_key(self.access_token)
        self._save(rds, key)


class RefreshToken(object):
    def __init__(self, **kwargs):
        if kwargs.has_key('uid'):
            self.user_id = kwargs.pop('uid')
        for k, v in kwargs.items():
            setattr(self, k, v)


    def load(self, rds, token):
        self.refresh_token = token
        key = refresh_token_key(token)
        return self._load(rds, key)


    def save(self, rds):
        key = refresh_token_key(self.refresh_token)
        self._save(rds, key)

    def _save(self, rds, key):
        logging.debug("save key:%s", key)
        pipe = rds.pipeline()
        m = {
            "token_type":self.token_type,
            "user_id":self.user_id,
        }
        pipe.hmset(key, m)
        pipe.execute()


    def _load(self, rds, key):
        t = rds.hmget(key, "token_type", "user_id")
        self.token_type, self.user_id = t
        return True if self.user_id else False

