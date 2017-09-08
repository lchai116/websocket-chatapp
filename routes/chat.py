from flask import Flask, render_template, request, session, redirect, url_for, Blueprint
import json
from . import *


main = Blueprint('main', __name__)


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


@main.route('/login', methods=['post', 'get'])
def chat_login():
    if request.method == 'POST':
        session['username'] = request.form.get('username', 'guest')
        i = randint(0,5)
        avatar_map[session['username']] = avatar_list[i]
        print session['username'] + ' new session name got'
        return redirect(url_for('.chat_index'))
    else:
        print session.get('username', 'empytsession') + 'session when login get'
        return render_template('chat_login.html')


@main.route('/')
@main.route('/lobby')
def chat_index():
    if not session.get('username',''):
        return redirect(url_for('.chat_login'))
    else:
        print session['username'] + ' Now the session name is'
        cur_user = user_inst_by_name(session['username'])
        return render_template('chat_index.html', cur_user=cur_user, users_in_room=[])


@main.route('/channelMsg', methods=['POST'])
def get_channel_msg():
    form = request.form
    cur_channel = form.get('cur_channel')
    msgs_in_room = msg_from_redis(cur_channel)
    cur_user = session.get('username', 'guest')
    r = {
        'success': True,
        'data': {
            'msgs_in_room': msgs_in_room,
            'cur_channel': cur_user,
        }
    }
    return json.dumps(r)