import redis
import time
from random import randint


red = redis.Redis(host='127.0.0.1', port=6379, db=0)
avatar_map = {}
avatar_list = [
    '/static/img/avatar/avatar_default.png',
    '/static/img/avatar/avatar_default1.png',
    '/static/img/avatar/avatar_default2.png',
    '/static/img/avatar/avatar_default3.png',
    '/static/img/avatar/avatar_default4.png',
    '/static/img/avatar/avatar_default5.png',
]


def timestamp():
    return int(time.time())


def user_inst_by_name(username):
    if not avatar_map.get(username):
        avatar_map[username] = avatar_list[randint(0,5)]
    r = {
            'username': username,
            'avatar': avatar_map[username],
    }
    return r