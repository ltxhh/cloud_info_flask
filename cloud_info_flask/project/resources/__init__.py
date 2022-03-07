from flask import Flask
from common.models import db
from flask_restful import Api
from flask_cors import CORS
def create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    api = Api(app)
    return app
