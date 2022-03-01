from common.models import db


# 专业表
class Sub(db.Model):
    __tablename__ = 'sub'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), doc='专业名称')
    stu = db.relationship('Stu', backref='stu', uselist=True)


# 学生表
class Stu(db.Model):
    __tablename__ = 'stu'
    stu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    age = db.Column(db.Integer)
    snum = db.Column(db.Integer, unique=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('sub.id'))
