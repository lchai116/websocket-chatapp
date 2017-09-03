from flask import Flask, render_template, request, session, redirect, url_for
import flask
import time
import socket, Queue, os, json
import redis
from flask_socketio import SocketIO, emit, disconnect, join_room
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'luch'
socketio = SocketIO(app, message_queue='redis://localhost:6379/0')
#socketio = SocketIO(app)
red = redis.Redis(host='127.0.0.1', port=6379, db=0)
pubsub = red.pubsub()
redis_channel = 'chat'
thread=None
avatar_map = {}
avatar_list = [
    '/static/img/avatar/avatar_default.png',
    '/static/img/avatar/avatar_default1.png',
    '/static/img/avatar/avatar_default2.png',
    '/static/img/avatar/avatar_default3.png',
    '/static/img/avatar/avatar_default4.png',
    '/static/img/avatar/avatar_default5.png',
]


def user_inst_by_name(username):
    if not avatar_map.get(username):
        avatar_map[username] = avatar_list[randint(0,5)]
    r = {
            'username': username, 
            'avatar': avatar_map[username],
    }
    return r


def timestamp():
    return int(time.time())


def msg_from_redis(channel):
    ms = []
    num = red.get('message:{}:count'.format(channel))
    num = 0 if not num else int(num)
    print 'message:{}:count got {} msgs'.format(channel, num)
    j = num if num < 10 else 10
    for i in range(num)[-j:]:
        m_dict = red.hgetall('message:{}:{}'.format(channel, str(i+1)))
        m_dict['username'] = m_dict['username'].decode('utf-8')
        m_dict['content'] = m_dict['content'].decode('utf-8')
        ms.append(m_dict)
    return ms


def msg_to_redis(msg_dict):
    channel = msg_dict['cur_channel']
    msg_id = str(red.incr('message:{}:count'.format(channel)))
    msg_key = 'message:{}:{}'.format(channel, msg_id)
    red.hmset(msg_key, msg_dict)


def members_set_from_db(channel):
    us = []
    user_in_room = list(red.smembers('channel:{}:members'.format(channel)))
    for u in user_in_room:
        user_inst = user_inst_by_name(u)
        us.append(user_inst)
    return us


def my_handler(r):
    print 'red callbak'
    print type(r)
    print r
    resp = r['data']
    print type(resp)
    print resp
    emit('myresp', json.loads(resp), room='Lobby')


@app.route('/chat/login', methods=['post', 'get'])
def chat_login():
    if request.method == 'POST':
        #print session['username'] + 'before empy'
        session['username'] = request.form.get('username', 'guest')
        i = randint(0,5)
        avatar_map[session['username']] = avatar_list[i]
        print session['username'] + ' new session name got'
        return redirect(url_for('.chat_index'))
    else:
        print session.get('username', 'empytsession') + 'session when login get'
        return render_template('chat_login.html')


@app.route('/chat/')
@app.route('/chat/lobby')
def chat_index():
    if not session.get('username',''):
        return redirect(url_for('.chat_login'))
    else:
        print session['username'] + ' Now the session name is'
        #ms = msg_from_redis()
        cur_user = user_inst_by_name(session['username'])
        return render_template('chat_index.html', cur_user=cur_user, users_in_room=[])


@app.route('/chat/channelMsg', methods=['POST'])
def get_channel_msg():
    form = request.form
    cur_channel = form.get('cur_channel')
    msgs_in_room = msg_from_redis(cur_channel)
   # users_in_room = members_set_from_db(cur_channel)
    cur_user = session.get('username', 'guest')
    r = {
        'success': True,
        'data': {
            'msgs_in_room': msgs_in_room,
        #    'users_in_room': users_in_room,
            'cur_channel': cur_user,
        }
    }
    return json.dumps(r)


@socketio.on('connect')
def srv_connect():
    print 'sock_conn luch'


@socketio.on('joined', namespace='/chat/lobby')
def joined(message):
    username = session.get('username')
    cur_channel = message['cur_channel']
    join_room(cur_channel)
    print 'joined ' + cur_channel
    emit('stat-tst', {'msg': session.get('username') + ' has entered the room.'})
    print 'before sadd' + cur_channel + username
    if not red.sismember('channel:{}:members' + cur_channel, username):
        # not in set, need to be added
        print 'sadd' + cur_channel
        red.sadd('channel:{}:members'.format(cur_channel), username)
        #avatar_map[username] = avatar_list[randint(0,5)]
        #num_member = red.scard('channel:{}:members'.format(cur_channel))
        member_in_room = members_set_from_db(cur_channel)
        emit('member update', {'member_in_room': member_in_room}, room=cur_channel)


@socketio.on('chat', namespace='/chat/lobby')
def handle_chat(message):
    print 'enter btn'
    print message
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
    # store the msg record in redis
    ## msg_to_redis(r)
    emit('myresp', r, room=cur_channel)
    print r
    #red.publish(redis_channel, json.dumps(r))


@socketio.on('close broadcast', namespace='/chat/lobby')
def close_broadcaset(data):
    cur_channel = data.get('cur_channel')
    username = session.get('username')
    red.srem('channel:{}:members'.format('lobby'), username)
    red.srem('channel:{}:members'.format('room1'), username)
    red.srem('channel:{}:members'.format('room2'), username)

    member_in_room = members_set_from_db(cur_channel)
    print 'close broad'
    emit('member update', {'member_in_room': member_in_room}, room=cur_channel)


@socketio.on('disconnect')
def srv_disconnect():
    print 'Client disconnected'


if __name__ == '__main__':
    config = dict(
        host='',
        port=5000,
        debug=True,
    )
#    app.run(**config)
    socketio.run(app, **config)
