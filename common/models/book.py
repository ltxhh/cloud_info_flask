# -*- codeing = utf-8 -*-
# @Time : 2022/3/28 20:49
# @Author : linyaxuan
# @File : book.py
# @Software : PyCharm
from common.models import db

from datetime import datetime


class Book(db.Model):
    """
    书籍
    """
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, doc='book_id')
    title = db.Column(db.String(32))
    pub_date = db.Column(db.DateTime, default=datetime.now)
    read = db.Column(db.Integer)
    comment = db.Column(db.Integer)
    is_delete = db.Column(db.Integer, default=0, doc='1表示删除0表示未删除')