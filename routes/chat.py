from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Blueprint

import json

from . import *


main = Blueprint('main', __name__)


def msg_from_redis(channel):
    ms = []
    # get msg number from string msg:channel:count
    num = red.get('message:{}:count'.format(channel))
    num = 0 if not num else int(num)
    # select 10 msg record from db
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
        uname = request.form.get('username', 'guest')
        session['username'] = uname
        # allocate a random avatar for the logging user, if name exists
        name_avatar_map[uname] = random.choice(avatar_list)
        return redirect(url_for('.chat_index'))
    else:
        if not request.form.get('username'):
            return render_template('chat_login.html')
        else:
            return redirect(url_for('.chat_index'))


@main.route('/')
@main.route('/lobby')
def chat_index():
    uname = session.get('username','')
    if not uname:
        return redirect(url_for('.chat_login'))
    else:
        cur_user = user_inst_by_name(uname)
        return render_template('chat_index.html', cur_user=cur_user, users_in_room=[])


@main.route('/channelMsg', methods=['POST'])
def get_channel_msg():
    form = request.form
    cur_channel = form.get('cur_channel')
    # loading msg record from db when enter the room
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