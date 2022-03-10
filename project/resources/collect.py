from common.models.models import News, db, Collection
from common.utils.login_utils import login_required

from flask import Blueprint, g
from flask_restful import reqparse, Api, fields, marshal

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


class Collect(RuntimeError):
    """
    收藏的orm操作
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        args = parser.parse_args()
        news_id = args.get('nid')
        user_id = g.user_id()
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
        parser.add_argument('nid', 'is_delete')
        args = parser.parse_args()
        news_id = args.get('nid')
        is_delete = args.get('is_delete')

        news = News.query.filter_by(nid=news_id).first()
        if news:
            Collection.query.filter_by(news_id=news_id).update({'is_delete': is_delete})
            db.session.commit()
            return {'code': 200, 'msg': ''}
        return {'code': 200, 'msg': 'Not find news'}


api.add_resource(Collect, '/user_collect')
