import redis
import time
import random


red = redis.Redis(host='127.0.0.1', port=6379, db=1)
name_avatar_map = {}
avatar_list = ['/static/chat/img/avatar/avatar_default{}.png'.format(i) for i in range(10)]


def timestamp():
    return int(time.time())


def user_inst_by_name(username):
    # in case the avatar is not stored in the backend
    if not name_avatar_map.get(username):
        name_avatar_map[username] = random.choice(avatar_list)
    r = {
            'username': username,
            'avatar': name_avatar_map[username],
    }
    return r