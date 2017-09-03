from flask_socketio import SocketIO
from flask import Flask
app = Flask(__name__)
socketio = SocketIO(message_queue='redis://localhost:6379/0')
print socketio

r = dict(
    name='luch',
    content='content',
    creattime='12345',
)
socketio.emit('queue_msg', r)