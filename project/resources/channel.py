# import traceback
from common.models.models import User, db, Channel, News, Comment
from common.utils.login_utils import login_required
from flask import Blueprint, g
from flask_restful import Api, Resource, reqparse, marshal, fields
from sqlalchemy import or_

text_bp = Blueprint('text', __name__)
api = Api(text_bp)
# 定义序列化字段
users_fields = {
    'uid': fields.Integer,
    'account': fields.String,
    'password': fields.String,
    'mobile': fields.String,
    'user_name': fields.String,
    'is_media': fields.Integer
}
channel_fields = {
    'cid': fields.Integer,
    'cname': fields.String,
    'ctime': fields.DateTime,
    'utime': fields.DateTime,
    'sequence': fields.Integer,
    'is_visible': fields.Boolean,
    'is_default': fields.Boolean,
}
title_fields = {
    'nid': fields.Integer,
    'user_id': fields.Integer,
    'channel_id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
}
comment_fields = {
    'cmid': fields.Integer,
    'user_id': fields.Integer,
    'article_id': fields.Integer,
    'content': fields.String,
}


class UserOrm(Resource):
    """
    用户的操作（增删改）
    parser.add_argument() ：添加校验参数
    args = parser.parse_args() ：校验
    marshal() 返回 json 数据
    """

    def post(self):
        parser = reqparse.RequestParser()
        lis = ['account', 'password', 'mobile', 'email']
        for i in lis:
            parser.add_argument(i)
        parser.add_argument('is_media')
        args = parser.parse_args()
        media = args.get('is_media')
        if media is '':
            is_media = 0
        else:
            is_media = 1
        account = args.get('account')
        password = args.get('password')
        mobile = args.get('mobile')
        email = args.get('email')
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        num = User.query.filter_by(mobile=mobile).count()
        if num >= 1:
            return [{'code': 400, 'msg': '该号码已注册过'}]
        num1 = User.query.filter_by(account=account).count()
        if num1 >= 1:
            return [{'code': 400, 'msg': '该账号已存在'}]
        user = User()
        user.account = account
        user.password = password
        user.email = email
        user.mobile = mobile
        user.is_media = is_media
        db.session.add(user)
        db.session.commit()
        return [marshal(user, users_fields)]

    def put(self):
        parser = reqparse.RequestParser()
        lis = ['account', 'password', 'mobile', 'is_media', 'uid', 'email']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        media = args.get('is_media')
        account = args.get('account')
        password = args.get('password')
        mobile = args.get('mobile')
        email = args.get('email')
        uid = args.get('uid')
        user = User.query.filter_by(uid=uid).first()
        user.is_media = int(media)
        user.mobile = mobile
        user.password = password
        user.email = email
        user.account = account
        db.session.commit()
        return [marshal(user, users_fields)]

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uid')
        args = parser.parse_args()
        uid = int(args.get('uid'))
        try:
            user = User.query.filter_by(uid=uid).delete()
            db.session.commit()
            return [marshal(user, users_fields)]
        except:
            return [{'code': 400, 'msg': '该用户不存在'}]


class ChannelOrm(Resource):
    """
    新闻频道的操作(增删改)
    parser.add_argument() ：添加校验参数
    args = parser.parse_args() ：校验
    marshal() 返回 json 数据
    """
    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        lis = ['cname', 'ctime', 'utime', 'sequence', 'is_visible', 'is_default']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        account = g.account
        cname = args.get('cname')
        ctime = args.get('ctime')
        utime = args.get('utime')
        sequence = args.get('sequence')
        is_visible = int(args.get('is_visible'))
        is_default = int(args.get('is_default'))
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        num = Channel.query.filter_by(cname=cname).count()
        if num >= 1:
            return [{'code': 400, 'msg': '该频道已存在'}]
        channel = Channel()
        channel.cname = cname
        channel.ctime = ctime
        channel.utime = utime
        channel.sequence = sequence
        channel.is_visible = is_visible
        channel.is_default = is_default
        db.session.add(channel)
        db.session.commit()
        return [marshal(channel, channel_fields)]

    def put(self):
        parser = reqparse.RequestParser()
        lis = ['cname', 'ctime', 'utime', 'sequence', 'is_visible', 'is_default', 'cid']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        cname = args.get('cname')
        cid = int(args.get('cid'))
        ctime = args.get('ctime')
        utime = args.get('utime')
        sequence = args.get('sequence')
        is_visible = int(args.get('is_visible'))
        is_default = int(args.get('is_default'))
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        try:
            channel = Channel.query.filter_by(cid=cid).first()
        except:
            return [{'code': 404, 'msg': '该频道不存在'}]
        channel.cname = cname
        channel.ctime = ctime
        channel.utime = utime
        channel.sequence = sequence
        channel.is_visible = is_visible
        channel.is_default = is_default
        db.session.commit()
        return [marshal(channel, channel_fields)]

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cid')
        args = parser.parse_args()
        cid = int(args.get('cid'))
        try:
            channel = Channel.query.filter_by(cid=cid).delete()
            db.session.commit()
            return [marshal(channel, channel_fields)]
        except:
            return [{'code': 400, 'msg': '该用户不存在'}]

    def get(self):
        info = Channel.query.all()
        return {'code': 200, 'msg': 'ok', 'data': marshal(info, channel_fields, envelope='channel')}


class TitleOrm(Resource):
    """
    文章(的增删改)
    parser.add_argument() ：添加校验参数
    args = parser.parse_args() ：校验
    marshal() 返回 json 数据
    """

    def post(self):
        parser = reqparse.RequestParser()
        lis = ['user_id', 'channel_id', 'title', 'content']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        user_id = args.get('user_id')
        channel_id = args.get('channel_id')
        title = args.get('title')
        content = args.get('content')
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        # num = News.query.filter_by(title=title).count()
        # if num >= 1:
        #     return [{'code': 400, 'msg': '该频道已存在'}]
        news = News()
        news.user_id = int(user_id)
        news.channel_id = int(channel_id)
        news.title = title
        news.content = content
        db.session.add(news)
        db.session.commit()
        return [marshal(news, title_fields)]

    def put(self):
        parser = reqparse.RequestParser()
        lis = ['user_id', 'channel_id', 'title', 'content', 'nid']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        nid = int(args.get('nid'))
        user_id = args.get('user_id')
        channel_id = args.get('channel_id')
        title = args.get('title')
        content = args.get('content')
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        try:
            news = News.query.filter_by(nid=nid).first()
        except:
            return [{'code': 404, 'msg': '该频道不存在'}]
        news.user_id = int(user_id)
        news.channel_id = int(channel_id)
        news.title = title
        news.content = content
        db.session.commit()
        return [marshal(news, title_fields)]

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid')
        args = parser.parse_args()
        nid = int(args.get('nid'))
        try:
            news = News.query.filter_by(nid=nid).delete()
            db.session.commit()
            return [marshal(news, title_fields)]
        except:
            return [{'code': 400, 'msg': '该文章不存在'}]

    def get(self):
        info = News.query.get()
        return {'code': 200, 'msg': 'ok', 'data': marshal(info, title_fields, envelope='news')}


class CommentOrm(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        lis = ['user_id', 'article_id', 'content']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        user_id = args.get('user_id')
        article_id = args.get('article_id')
        content = args.get('content')
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        # num = News.query.filter_by(title=title).count()
        # if num >= 1:
        #     return [{'code': 400, 'msg': '该频道已存在'}]
        comment = Comment()
        comment.user_id = int(user_id)
        comment.article_id = int(article_id)
        comment.content = content
        db.session.add(comment)
        db.session.commit()
        return [marshal(comment, comment_fields)]

    def put(self):
        parser = reqparse.RequestParser()
        lis = ['user_id', 'article_id', 'content', 'cmid']
        for i in lis:
            parser.add_argument(i)
        args = parser.parse_args()
        user_id = args.get('user_id')
        cmid = args.get('cmid')
        article_id = args.get('article_id')
        content = args.get('content')
        for info in args:
            lens = len(args[info])
            if lens == 0:
                data = f'{info}'.format(info=info)
                return [{'data': 400, 'msg': data}]
        try:
            comment = Comment.query.filter_by(cmid=cmid).first()
        except:
            return [{'code': 404, 'msg': '该评论不存在'}]
        comment.user_id = int(user_id)
        comment.article_id = int(article_id)
        comment.content = content
        db.session.commit()
        return [marshal(comment, comment_fields)]

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('cmid')
        args = parser.parse_args()
        cmid = int(args.get('cmid'))
        try:
            comment = Comment.query.filter_by(cmid=cmid).delete()
            db.session.commit()
            return [marshal(comment, comment_fields)]
        except:
            return [{'code': 400, 'msg': '该评论不存在'}]

    def get(self):
        info = Comment.query.get()
        return {'code': 200, 'msg': 'ok', 'data': marshal(info, comment_fields, envelope='comment')}


class FuzzyEnquiry(Resource):
    """
    模糊查询（用户）
    """

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('keys', location='form')
        args = parser.parse_args()
        keys = args.get('keys')
        print(keys)
        info = User.query.filter(or_(
            User.account.like("%{keys}%".format(keys=keys)),
            User.mobile.like('%{keys}%'.format(keys=keys))
        )).all()
        return {'msg': 'ok', 'code': 200, 'data': marshal(info, users_fields, envelope='channel')}


api.add_resource(UserOrm, '/users')
api.add_resource(ChannelOrm, '/channel')
api.add_resource(TitleOrm, '/news')
api.add_resource(CommentOrm, '/comment')
api.add_resource(FuzzyEnquiry, '/get_info')
