from flask import Flask
from common.models import db
from project.resources.stu import stu


def Create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(stu)
    return app


