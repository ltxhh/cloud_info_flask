from flask import Flask
from common.models import db
from flask_restful import Api
from flask_cors import CORS
from project.resources.users import user_bp
from project.resources.channel import text_bp
from project.resources.userChannels import channels_bp
from project.resources.news import news_bp
from logs.logs import setup_log
import redis
from common.utils.middlewares import jwt_authentication


def create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.before_request(jwt_authentication)
    app.register_blueprint(user_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(channels_bp)
    setup_log('testing')
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Api(app)
    return app