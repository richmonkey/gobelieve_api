import time
def verify_code_key(zone, number):
    assert(zone and number)
    return "vc_" + zone + "-" + number

def set_verify_code(rds, zone, number, code):
    now = int(time.time())
    key = verify_code_key(zone, number)
    count = rds.hget(key, 'count')
    count = int(count) if count else 0
    pipe = rds.pipeline()
    if count > 10:
        pipe.hset(key, 'count', '1')
    else:
        pipe.hincrby(key, 'count')
    m = {
        'last_timestamp':now,
        'code':code,
    }
    pipe.hmset(key, m)
    pipe.execute()

def get_verify_code(rds, zone, number):
    key = verify_code_key(zone, number)
    last_timestamp, code, count = rds.hmget(key, 'last_timestamp', 'code', 'count')
    last_timestamp = int(last_timestamp) if last_timestamp else 0
    count = int(count) if count else 0
    return code, last_timestamp, count
