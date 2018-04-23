from flask import Flask
from routes.events import socketio
from routes.chat import main as chat_bp


app = Flask(__name__)


def register_routes():
    app.register_blueprint(chat_bp, url_prefix='/chat')


def configure_app():
    app.secret_key = '#1234'
    socketio.init_app(app)
    register_routes()


def create_app():
    configure_app()
    return app


if __name__ == '__main__':
    config = dict(
        host='',
        port=5000,
        debug=True,
    )
    configure_app()
    socketio.run(app, **config)
