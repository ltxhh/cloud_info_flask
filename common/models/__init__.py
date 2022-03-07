from flask_sqlalchemy import SQLAlchemy
import redis
from common.settings.default import Redis
rds = Redis().connect()
db = SQLAlchemy()

