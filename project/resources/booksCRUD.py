# -*- codeing = utf-8 -*-
# @Time : 2022/3/28 20:57
# @Author : linyaxuan
# @File : booksCRUD.py
# @Software : PyCharm

from common.models.book import Book
from flask import Blueprint, g
from common.models import db

from flask import Blueprint
from flask_restful import Api, Resource, marshal, reqparse
from common.utils.custom_output_json import custom_output_json
from common.model_fields.book_fields import book_fields

books_bp = Blueprint('books', __name__)
api = Api(books_bp)


@api.representation('application/json')
def output_json(data, code=200, headers=None):
    return custom_output_json(data, code, headers)


class BookCRUD(Resource):
    """
    书籍的增删改查
    """
    def get(self):
        books_list = Book.query.filter_by(is_delete=0).order_by(Book.pub_date.desc()).all()
        return marshal(books_list, book_fields)

    def post(self):
        """
        添加书籍
        """
        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('read', 0)
        parser.add_argument('comment', 0)
        parser.add_argument('is_delete', 0)
        args = parser.parse_args()
        book = Book()
        book.title = args.get('title')
        book.read = args.get('read')
        book.comment = args.get('comment')
        book.is_delete = args.get('is_delete')
        db.session.add(book)
        db.session.commit()
        return marshal(book, book_fields)

    def put(self):
        """
        修改书籍名称
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('id')
        args = parser.parse_args()
        title = args.get('title')
        id = args.get('id')
        book = Book.query.get(id)
        if not book:
            return {'message': 'book is not exist!', 'code': 405}
        book.title = title
        db.session.commit()
        return marshal(book, book_fields)

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id')
        args = parser.parse_args()
        id = args.get('id')
        book = Book.query.get(id)
        if not book:
            return {'message': 'book is not exist!', 'code': 405}
        book.is_delete = 1
        db.session.commit()
        return marshal(book, book_fields)


api.add_resource(BookCRUD, '/book_crud', endpoint='book_crud')
