class User:
    def __init__(self):
        self.uid = None
        self.state = None
        self.avatar = None

def user_key(uid):
    return "users_" + str(uid)

def get_user(rds, uid):
    u = User()
    key = user_key(uid)
    u.state, u.avatar = rds.hmget(key, "state", "avatar")
    if u.state is None and u.avatar is None:
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
    pipe.execute()

