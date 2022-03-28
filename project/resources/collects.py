# coding: utf-8

from common.models.models import News, db, Collection, User
from common.utils.login_utils import login_required

from flask import Blueprint, g
from flask_restful import reqparse, Api, fields, marshal, Resource

collect_bp = Blueprint('collect', __name__)
api = Api(collect_bp)

# 序列化字段
news_fields = {
    'nid': fields.Integer,
    'user_id': fields.Integer,
    'channel_id': fields.Integer,
    'title': fields.String,
    'content': fields.String
}


class CollectOrm(Resource):
    """
    收藏的orm操作
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        args = parser.parse_args()
        news_id = args.get('nid')
        user_id = g.user_id
        news = News.query.filter_by(nid=news_id).first()
        if news:
            collect = Collection()
            collect.user_id = user_id
            collect.news_id = news_id
            db.session.add(collect)
            # user = User.query.get(user_id)
            # news.user.append(user)
            db.session.commit()
            return {'code': 201, 'news': marshal(news, news_fields, envelope='data')}
        return {'code': 200, 'msg': 'Not find news '}

    @login_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        parser.add_argument('is_delete')
        args = parser.parse_args()
        news_id = args.get('nid')
        is_delete = args.get('is_delete')
        user_id = g.user_id
        news = News.query.filter_by(nid=news_id).first()
        if news:
            collect = Collection.query.filter_by(news_id=news_id, user_id=user_id).first()
            collect.is_delete = int(is_delete)
            db.session.add(collect)
            db.session.commit()
            return {'code': 200, 'msg': ''}
        return {'code': 200, 'msg': 'Not find news'}

    @login_required
    def get(self):
        """
        page： 当前页数
        page_size: 每页显示几个数据
        """
        parser = reqparse.RequestParser()
        parser.add_argument('page', location='form')
        parser.add_argument('page_size', location='form')
        args = parser.parse_args()
        page = int(args.get('page'))
        page_size = int(args.get('page_size'))
        user_id = g.user_id
        user = User.query.get(user_id)
        news = user.collection
        num = Collection.query.filter_by(user_id=user_id).count()
        start = (page - 1) * page_size
        end = page * page_size if num > page * page_size else page * page_size
        news = news[start: end]
        return {'code': 200, 'news': marshal(news, news_fields, envelope='data')}


class GetNewList(Resource):
    """
    获取资讯列表
    """

    @login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('page', default=1, type=int)
        parser.add_argument('page_size', default=20, type=int)
        args = parser.parse_args()
        page = args.get('page')
        page_size = args.get('page_size')
        news = News.query.all()
        page_size = page_size if 30 > page_size > 10 else 20
        news.reverse()
        count = len(news)
        start = (page - 1) * page_size
        end = page * page_size if count > page * page_size else page * page_size
        news_list = news[start:end]
        return {'code': 200, 'news': marshal(news_list, news_fields)}


api.add_resource(CollectOrm, '/user_collect')
api.add_resource(GetNewList, '/news_list')
