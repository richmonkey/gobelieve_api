import logging
class Contact:
    def __init__(self):
        self.name = None
        self.uid = None
    def to_string(self):
        return "%d_%s"%(self.uid, self.name)
    def from_string(self, s):
        self.uid, self.name = s.split("_", 1)
        
class User:
    def __init__(self):
        self.uid = None
        self.state = None
        self.avatar = None
        self.apns_device_token = None
        self.up_timestamp = None
        self.ng_device_token = None
        self.face_apns_device_token = None
        self.face_ng_device_token = None

def user_key(uid):
    return "users_" + str(uid)

def get_user(rds, uid):
    u = User()
    key = user_key(uid)
    u.state, u.avatar, u.apns_device_token, u.ng_device_token, u.up_timestamp, \
        u.face_apns_device_token, u.face_ng_device_token \
        = rds.hmget(key, "state", "avatar", "apns_device_token", \
                    "ng_device_token", "up_timestamp", \
                    "face_apns_device_token", "face_ng_device_token")
    if u.state is None and u.avatar is None and \
       u.apns_device_token is None and \
       u.ng_device_token is None and \
       u.up_timestamp is None and \
       u.face_apns_device_token is None and \
       u.face_ng_device_token is None:
        return None
    u.uid = uid
    if u.up_timestamp:
        u.up_timestamp = int(u.up_timestamp)
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
        #clear ng device token
        pipe.hset(key, "ng_device_token", "")
    elif user.ng_device_token:
        pipe.hset(key, "ng_device_token", user.ng_device_token)
        #clear apns device token
        pipe.hset(key, "apns_device_token", "")
    elif user.face_apns_device_token:
        pipe.hset(key, "face_apns_device_token", user.face_apns_device_token)
        pipe.hset(key, "face_ng_device_token", "")
    elif user.face_ng_device_token:
        pipe.hset(key, "face_ng_device_token", user.face_ng_device_token)
        pipe.hset(key, "face_apns_device_token", "")
        
    pipe.execute()

def set_user_contact_list(rds, uid, contacts):
    if not contacts:
        return

    id_key = "user_contact_ids_%s"%uid
    name_key = "user_contact_names_%s"%uid
    ids = []
    names = []
    for c in contacts:
        ids.append(c.uid)
        names.append(c.name)
    pipe = rds.pipeline()
    pipe.delete(id_key)
    pipe.rpush(id_key, *tuple(ids))
    pipe.delete(name_key)
    pipe.rpush(name_key, *tuple(names))
    pipe.execute()

def get_user_contact_list(rds, uid):
    id_key = "user_contact_ids_%s"%uid
    name_key = "user_contact_names_%s"%uid

    contacts = []
    pipe = rds.pipeline()
    pipe.lrange(name_key, 0, -1)
    pipe.lrange(id_key, 0, -1)
    names, ids = pipe.execute()

    if len(names) != len(ids):
        logging.error("name count is't equal id count")
        return contacts

    for i, uid in enumerate(ids):
        contact = Contact()
        contact.uid = uid
        contact.name = names[i]
        contacts.append(contact)

    return contacts
        

def set_user_state(rds, uid, state):
    key = user_key(uid)    
    rds.hset(key, "state", state)

def set_user_avatar(rds, uid, avatar):
    key = user_key(uid)
    rds.hset(key, "avatar", avatar)

def make_uid(zone, number):
    return int(zone+"0"+number)
