# coding: =utf-8


import logging
import traceback
from common.models.models import News, db, User, Channel, Comment
from common.cache import cache
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
    'content': fields.String,
    'good_count': fields.Integer,
}


class NewsOrm(Resource):
    """
    咨询的orm操作
    """

    @login_required
    def get(self):
        user_id = g.user_id
        try:
            news = News.query.filter_by(user_id=user_id, status=1).all()
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

    @cache.cached(timeout=60)
    def _get_like(self):
        user = User.query.all()
        channels = user.channels
        info = {}
        news_list = cache.get('news_list')
        if news_list:
            return news_list
        for channel in channels:
            news = News.query.filter_by(channel_id=channel.cid).order_by(News.good_count.desc())
            news = news.first()
            if news:
                cache.set('news_list', news, timeout=60 * 5)
        return info.update(news)
        # user = User.query.all()
        # channels = user.channels
        # info = {}
        # try:
        #     for channel in channels:
        #         news = channel.news
        #         info.update({channel.cname: news})
        # except:
        #     return {'code': 500, 'msg': 'err'}
        # return info

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
            channel = Channel.query.filtery_by(channel_id=channel_id, status=1).all()
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
        news = cache.get('news_{}'.format(nid))
        if not news:
            news = News.query.get(nid)
            news = cache.set('news_{}'.format(nid), news, timeout=30)
        logging.debug('debug')
        logging.error('err')
        return {'code': 200, 'news': marshal(news, news_fields, envelope='data')}


class UserGiveTheThumbsUp(Resource):
    """
    文章点赞
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        args = parser.parse_args()
        nid = args.get('nid')
        new = News.query.get(nid)
        if new:
            new.good_count += 1
            db.session.commit()
            return {'code': 200, 'news': marshal(new, news_fields, envelope='data')}
        return {'code': 200, 'msg': 'parameter error'}


comment_fields = {
    'cmid': fields.Integer,
    'user_id': fields.Integer,
    'article_id': fields.Integer,
    'content': fields.String,
    'parent_id': fields.Integer
}


class CommentCRUD(Resource):
    """
    文章评论的 CRUD
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        lis = ['article_id', 'content']
        for arg in lis:
            parser.add_argument(arg)
        parser.add_argument('parent_id')
        args = parser.parse_args()
        data = {'user_id': g.user_id}
        try:
            for k in args:
                value = args.get(k)
                if value:
                    data.update({k: value})
            if args.get('parent_id') and \
                    Comment.query.filter_by(parent_id=args.get('parent_id')).all():
                data.update({'parent_id': args.get('parent_id')})

            comment = Comment(**data)
            db.session.add(comment)
            db.session.commit()
            return {'code': 200, 'comment': marshal(comment, comment_fields, envelope='data')}
        except:
            error = traceback.format_exc()
            logging.debug('debuge {}'.format(error))
            return {'code': 500, 'msg': 'error'}

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('article_id', location='form')
        args = parser.parse_args()
        article_id = args.get('article_id')
        try:
            comment = Comment.query.filter_by(article_id=article_id).all()
            return {'code': 200, 'comment': marshal(comment, comment_fields, envelope='data')}
        except:
            error = traceback.format_exc()
            logging.debug('debuge {}'.format(error))
            return {'code': 500, 'msg': 'error'}

    @login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('article_id')
        args = parser.parse_args()
        article_id = args.get('article_id')
        user_id = g.user_id


class AdminStart(Resource):
    """
    超级管理员
    """

    def post(self):
        parser = reqparse.RequestParser()
        lis = ['account', 'mobile', 'password']
        for i in lis:
            parser.add_argument(i)
        parser.add_argument('Administrator', type=int)
        args = parser.parse_args()
        for k in args:
            lens = len(args.get(k))
            if lens == 0:
                data = f"{k} is None".format(k=k)
                return {'code': 200, 'msg': data}
        if args.get('Administrator') != 1 or args.get('Administrator') != 0:
            return {'code': 200, 'msg': 'error! Administrator must 1 or 0'}
        if User.query.filter_by(mobile=args.get('mobile')).all():
            return {'code': 200, 'msg': 'The mobile number is registered'}
        if User.query.filter_by(account=args.get('account')).all():
            return {'code': 200, 'msg': 'The account has been registered'}
        user = User()
        user.account = args.get('account')
        user.password = args.get('password')
        user.mobile = args.get('mobile')
        user.Administrator = args.get('Administrator')
        db.session.add(user)
        db.session.commit()
        return {'code': 200, 'data': 'successfully added '}

    @login_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Administrator', type=int)
        args = parser.parse_args()
        uid = g.user_id

        if args.get('Administrator') != 1 or args.get('Administrator') != 0:
            return {'code': 200, 'msg': 'error! Administrator must 1 or 0'}
        user = User.query.get(uid)
        if user:
            user.Administrator = args.get('Administrator')
            db.session.add(user)
            db.session.commit()
            return {'code': 200, 'msg': 'Description The super administrator is successfully added'}


class AdminUserCRUD(Resource):
    @login_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid', type=int)
        args = parser.parse_args()
        nid = args.get('nid')
        uid = g.user_id
        user = User.query.get(uid)
        news = News.query.get(nid)
        if (user and user.Administrator == 1) or news.user_id == uid:
            if news:
                news.status = 0
                db.session.add(user)
                db.session.commit()
            return {'code': 200, 'msg': 'The information was deleted successfully'}


class UserStatus(Resource):
    """
    超级管理员封用户
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid')
        args = parser.parse_args()
        user_id = g.user_id
        super_user = User.query.get(user_id)
        if super_user:
            user = User.query.get(args.get('uid'))
            if user:
                user.status = 1
                db.session.commint()
                return {'code': 200, 'msg': 'The user is blocked successfully. Procedure'}
            return {'code': 400, 'msg': 'The user does not exist'}
        return {'code': 503, 'msg': 'You are not super administrator and do not have this permission'}


class NewsStatus(Resource):
    """
    超级管理员封文章
    """

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        args = parser.parse_args()
        user_id = g.user_id
        super_user = User.query.get(user_id)
        if super_user:
            news = News.query.get(args.get('nid'))
            if news:
                news.status = 1
                db.session.commint()
                return {'code': 200, 'msg': 'The news is blocked successfully. Procedure'}
            return {'code': 400, 'msg': 'The news does not exist'}
        return {'code': 503, 'msg': 'You are not super administrator and do not have this permission'}


class CommentsLike(Resource):
    """
    评论点赞
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        parser.add_argument('cmid')
        args = parser.parse_args()
        new = News.query.get(args.get('nid'))
        if new:
            comment = Comment.query.get(args.get('cmid'))
            if comment:
                comment.like_count += 1
                db.session.commit()
                return {'code': 200, 'msg': 'Successfully!'}
            return {'code': 200, 'msg': 'The comment does not exist'}
        return {'code': 500, 'msg': 'The article does not exist'}


api.add_resource(NewsOrm, '/news_orm')
api.add_resource(GetUserLike, '/get_user_like')
api.add_resource(GetNewChannel, '/get_user_channel')
api.add_resource(Consult, '/get_consult')
api.add_resource(UserGiveTheThumbsUp, '/user_like_count')
api.add_resource(CommentCRUD, '/commentCRUD')
api.add_resource(AdminStart, '/add_admin_user')
api.add_resource(AdminUserCRUD, '/new_put')
api.add_resource(UserStatus, '/user_status')
api.add_resource(NewsStatus, '/new_status')
api.add_resource(CommentsLike, '/comments_like')
