import demjson
from common.models.models import Channel, db, User, UserChannel
from flask import Blueprint, g
from flask_restful import Api, Resource, reqparse, marshal, fields
from common.utils.login_utils import login_required

channels_bp = Blueprint('userChannels', __name__)
api = Api(channels_bp)

# 序列化字段
user_channel_fields = {
    'cid': fields.Integer,
    'uid': fields.Integer,
    'is_delete': fields.Boolean,
    'create_time': fields.String,
    'update_time': fields.String,
    'sequence': fields.Integer
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


class UserChannelOrm(Resource):
    """
    用户频道的orm操作
    """

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('channel_list')
        parser.add_argument('is_delete')
        args = parser.parse_args()
        is_delete = args.get('is_delete')
        channel_list = demjson.decode(args['channel_list'])
        user_id = g.user_id
        for channel in channel_list:
            print(channel.get('cid'))
            cid = channel['cid']
            if Channel.query.filter_by(cid=cid).first() is None:
                return {'code': 200, 'msg': '未找到该频道'}
            else:
                channel = Channel.query.filter_by(cid=cid).first()
                user = User.query.filter_by(uid=user_id).first()
                info = channel.user
                if info == []:
                    channel.user.append(user)
                else:
                    return {'code': 200, 'msg': '该频道已存在'}
            db.session.commit()
        return {'code': 200, 'msg': 'ok', 'info': marshal(info, user_channel_fields, envelope='data')}

    @login_required
    def get(self):
        user_id = g.user_id
        print(user_id)
        user = User.query.get(user_id)
        info = user.channels
        return {'code': 200, 'info': marshal(info, channel_fields, envelope='data')}

    @login_required
    def delete(self):
        user_id = g.user_id
        parser = reqparse.RequestParser()
        parser.add_argument('cid')
        args = parser.parse_args()
        cid = args.get('cid')
        channel = Channel.query.filter_by(cid=cid).first()
        user = User.query.filter_by(uid=user_id).first()
        channel.user.remove(user)
        return 'ok'

    def put(self):
        user_id = g.user_id
        parser = reqparse.RequestParser()
        parser.add_argument('cid')


api.add_resource(UserChannelOrm, '/user_channel_orm')
