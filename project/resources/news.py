# coding: =utf-8


import logging
from common.models.models import News, db, User, Channel
from flask import Blueprint, g
from flask_restful import Api, Resource, reqparse, marshal, fields
from common.utils.login_utils import login_required

news_bp = Blueprint('news_bp', __name__)
api = Api(news_bp)

# 序列化字段
news_fields = {
    'nid': fields.Integer,
    'user_id': fields.Integer,
    'channel_id': fields.Integer,
    'title': fields.String,
    'content': fields.String
}


class NewsOrm(Resource):
    """
    咨询的orm操作
    """

    @login_required
    def get(self):
        user_id = g.user_id
        try:
            news = News.query.filter_by(user_id=user_id).all()
        except:
            return {'code': 200, 'msg': 'The query was not found'}
        return {'code': 200, 'news': marshal(news, news_fields, envelope='data')}

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        lis = ['title', 'channel_id', 'content']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        data = {'user_id': g.user_id}
        for i in args:
            value = args.get(i)
            if value:
                data.update({i: value})
        news = News(**data)
        db.session.add(news)
        # db.session.commit()w
        return {'code': 200, 'msg': 'add successful', 'news': marshal(news, news_fields)}


class GetUserLike(Resource):
    """
    用户喜欢的文章
    """

    def _get_user_like(self, user_id):
        user = User.query.get(user_id)
        channels = user.channels
        info = {}
        try:
            for channel in channels:
                news = channel.news
                info.update({channel.cname: news})
        except:
            return {'code': 200, 'msg': 'not find'}
        return info

    def _get_like(self):
        user = User.query.all()
        channels = user.channels
        info = {}
        try:
            for channel in channels:
                news = channel.news
                info.update({channel.cname: news})
        except:
            return {'code': 500, 'msg': 'err'}
        return info

    def get(self):
        user_id = g.user_id
        result = {}
        if user_id:
            result = self._get_user_like(user_id)
        else:
            result = self._get_like()
        return result


class GetNewChannel(Resource):
    """
    获取指定频道的前二十篇文章
    """

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_id', location='form')
        args = parser.parse_args()
        channel_id = int(args.get('channel_id'))
        if Channel.query.get(channel_id):
            channel = Channel.query.get(channel_id)
            print(channel)
            news_list = channel.news
            # news_list.reverse()
            if len(news_list) >= 20:
                new_list = news_list[19::-1]
                return {"code": 200, "new_list": marshal(new_list, news_fields)}
        return {"code": 200, "msg": 'The channel could not be found'}


class Consult(Resource):
    """
    获取咨询
    """

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid', location='form')
        args = parser.parse_args()
        nid = args.get('nid')
        news = News.query.get(nid)
        logging.debug('debug')
        logging.error('err')
        return {'code': 200, 'news': marshal(news, news_fields, envelope='data')}


api.add_resource(NewsOrm, '/news_orm')
api.add_resource(GetUserLike, '/get_user_like')
api.add_resource(GetNewChannel, '/get_user_channel')
api.add_resource(Consult, '/get_consult')
