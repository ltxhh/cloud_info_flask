from flask import Flask
from common.models import db
from flask_restful import Api
from flask_cors import CORS
from project.resources.users import user_bp
from project.resources.text import text_bp
import redis
from common.utils.middlewares import jwt_authentication


def create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.before_request(jwt_authentication)
    app.register_blueprint(user_bp)
    # app.register_blueprint(text_bp)
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Api(app)
    return app
