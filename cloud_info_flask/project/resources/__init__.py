from flask import Flask
from common.models import db


def create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    return app
