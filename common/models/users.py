from common.models import db


class User(db.Model):
    __tablename__ = 'name'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), doc='用户名')
    age = db.Column(db.Integer, doc='年龄')
