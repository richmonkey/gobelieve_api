class User:
    def __init__(self):
        self.uid = None
        self.state = None
        self.avatar = None
        self.apns_device_token = None

def user_key(uid):
    return "users_" + str(uid)

def get_user(rds, uid):
    u = User()
    key = user_key(uid)
    u.state, u.avatar, u.apns_device_token = rds.hmget(key, "state", "avatar", "apns_device_token")
    if u.state is None and u.avatar is None and u.apns_device_token is None:
        return None
    u.uid = uid
    return u

def save_user(rds, user):
    key = user_key(user.uid)
    pipe = rds.pipeline()
    if user.state:
        pipe.hset(key, "state", user.state)
    if user.avatar:
        pipe.hset(key, "avatar", user.avatar)
    if user.apns_device_token:
        pipe.hset(key, "apns_device_token", user.apns_device_token)
    pipe.execute()


def set_user_state(rds, uid, state):
    key = user_key(uid)    
    rds.hset(key, "state", state)

def make_uid(zone, number):
    return int(zone+"0"+number)
