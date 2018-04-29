from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import disconnect
from flask_socketio import join_room

from . import *


logger = logging.getLogger(__name__)
socketio = SocketIO()


def members_set_from_db(channel):
    us = []
    user_in_room = list(red.smembers('channel:{}:members'.format(channel)))
    for u in user_in_room:
        user_inst = user_inst_by_name(u)
        us.append(user_inst)
    return us


def msg_to_redis(msg_dict):
    channel = msg_dict['cur_channel']
    # msg counter  message:channel:msgid
    msg_id = str(red.incr('message:{}:count'.format(channel)))
    msg_key = 'message:{}:{}'.format(channel, msg_id)
    red.hmset(msg_key, msg_dict)


@socketio.on('connect')
def srv_connect():
    logger.info('sock_connected')


@socketio.on('joined', namespace='/chat/lobby')
def joined(message):
    username = session.get('username')
    cur_channel = message['cur_channel']
    join_room(cur_channel)
    emit('stat-tst', {'msg': session.get('username') + ' has entered the room.'})
    if not red.sismember('channel:{}:members' + cur_channel, username):
        red.sadd('channel:{}:members'.format(cur_channel), username)
        member_in_room = members_set_from_db(cur_channel)
        emit('member update', {'member_in_room': member_in_room}, room=cur_channel)


@socketio.on('chat', namespace='/chat/lobby')
def handle_chat(message):
    username = session.get('username', 'guest')
    content = message.get('content', '')
    cur_channel = message['cur_channel']
    r = dict(
        username=username,
        content=content,
        creattime=timestamp(),
        cur_channel=cur_channel,
        avatar=user_inst_by_name(username)['avatar']
    )
    # store the msg record into redis
    msg_to_redis(r)
    emit('myresp', r, room=cur_channel)


@socketio.on('close broadcast', namespace='/chat/lobby')
def close_broadcaset(data):
    cur_channel = data.get('cur_channel')
    username = session.get('username')
    session.pop('username', None)
    red.srem('channel:{}:members'.format('lobby'), username)
    red.srem('channel:{}:members'.format('room1'), username)
    red.srem('channel:{}:members'.format('room2'), username)

    member_in_room = members_set_from_db(cur_channel)
    logger.info('close broadcast')
    emit('member update', {'member_in_room': member_in_room}, room=cur_channel)


@socketio.on('disconnect')
def srv_disconnect():
    logger.info('Client disconnected')
