from datetime import datetime
from datetime import timedelta
import time
import logging

def access_token_key(token):
    return "access_token_" + token

def refresh_token_key(token):
    return "refresh_token_" + token

class Token(object):
    def __init__(self, **kwargs):
        if kwargs.has_key('expires_in'):
            expires_in = kwargs.pop('expires_in')
            self.expires = datetime.utcnow() + timedelta(seconds=expires_in)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def _save(self, rds, key):
        logging.debug("save key:%s", key)
        pipe = rds.pipeline()
        expires = int(time.mktime(self.expires.timetuple()))
        m = {
            "access_token":self.access_token,
            "refresh_token":self.refresh_token,
            "expires":expires,
            "token_type":self.token_type,
            "user_id":self.user_id,
        }
        pipe.hmset(key, m)
        pipe.execute()
        
    def save_access_token(self, rds):
        key = access_token_key(self.access_token)
        self._save(rds, key)

    def save_refresh_token(self, rds):
        key = refresh_token_key(self.refresh_token)
        self._save(rds, key)

    def save(self, rds):
        self.save_access_token(rds)
        self.save_refresh_token(rds)

    def _load(self, rds, key):
        t = rds.hmget(key, "access_token", "refresh_token", \
                      "expires", "token_type", "user_id")
        self.access_token, self.refresh_token, self.expires,\
            self.token_type, self.user_id = t
        if self.expires:
            self.expires = datetime.fromtimestamp(int(self.expires))
        logging.debug("load :%s key:%s", self.access_token, key)
        return True if self.access_token else False

class AccessToken(Token):
    def load(self, rds, token):
        key = access_token_key(token)
        return self._load(rds, key)


class RefreshToken(Token):
    def load(self, rds, token):
        key = refresh_token_key(token)
        return self._load(rds, key)


