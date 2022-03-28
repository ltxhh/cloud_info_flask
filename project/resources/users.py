import traceback
import logging
from common.models.models import User, db, Channel, News
from common.utils.jwt_utils import generate_jwt, _generate_token, refresh_token
from common.utils.login_utils import login_required
from common.models import rds
from common.cache import cache

from flask import Blueprint, g
from flask_restful import Api, Resource, reqparse, marshal, fields
from datetime import datetime, timedelta
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from common.utils.custom_output_json import custom_output_json
from common.model_fields.user_fields import user_fields

user_bp = Blueprint('users', __name__)
api = Api(user_bp)


@api.representations('application/json')
def output_json(data, code=200, headers=None):
    return custom_output_json(data, code, headers)


class SMSVerificationCodeResource(Resource):
    """
    验证码发送视图
    """

    def get(self):
        # 获取用户手机号码
        req = reqparse.RequestParser()
        req.add_argument('mobile', location='form')
        args = req.parse_args()
        mobile = args['mobile']
        # 给用户发送手机号码: ali-sdk
        client = AcsClient(
            "LTAI4G7FrRj37co9gGDFRfbX",
            "9NxJUZdNj7B21dJ627WuKYqc4MEuiV",
            "cn-hangzhou"
        )
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', "17679962330")
        request.add_query_param('SignName', "云资讯")
        request.add_query_param('TemplateCode', "SMS_211497619")
        response = client.do_action(request)
        print(str(response, encoding='utf-8'))
        # 连接Redis, 存储验证码
        rds.setex(mobile, 200, '852963')
        return {'message': 'ok', 'data': {'mobile': mobile}, 'code': 200}


class AuthorizationResource(Resource):
    """
    注册账号
    """

    def post(self):
        parser = reqparse.RequestParser()
        args_list = ['account', 'password', 'mobile', 'code']
        for i in args_list:
            parser.add_argument(i, required=True)
        args = parser.parse_args()
        account = args.get('account')
        password = args.get('password')
        mobile = args.get('mobile')
        # 验证码
        code = args.get('code')
        # 验证手机号是否已使用
        number = User.query.filter(User.mobile == mobile).first()
        print('11323421', number)
        if number is not None:
            return {'code': 405, 'result': '该手机已绑定用户，请更换手机号'}
        # 验证用户是否已经注册
        user_num = User.query.filter_by(account=account).count()
        if user_num >= 1:
            return {'code': 405, 'result': '该用户已存在'}
        # 添加手机验证码
        rds_code = rds.get(mobile)

        if not rds_code:
            return {'code': 406, 'result': '验证码过期，请重新发送验证'}
        # 从redis中获取的验证码为字节类型，需要转换成字符类型
        rds_code = rds_code.decode()
        # 校验手机验证码
        if rds_code != code:
            return {'code': 403, 'result': '验证码错误'}

        # 通过验证，注册用户
        user = User()
        user.account = account
        user.password = password
        user.mobile = mobile
        user.last_login = datetime.now()
        db.session.add(user)
        db.session.commit()
        return {'code': 200, 'data': marshal(user, user_fields)}


class Login(Resource):
    """
    登录
    """

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('account')
        parser.add_argument('password')
        args = parser.parse_args()
        account = args.get('account')
        password = args.get('password')

        # 判断用户账号密码是否正确
        user = User.query.filter_by(account=account, password=password).first()
        if not user:
            return {'code': 406, 'result': '用户名或密码错误'}
        user.last_login = datetime.now()
        db.session.commit()
        user_id = user.uid
        token, refresh_token = _generate_token(user_id)
        return {'code': 200, 'data': {'token': token, 'refresh_token': refresh_token}}


class RefreshToken(Resource):
    def put(self):
        return refresh_token()


class GetUserInfo(Resource):
    """
    获取用户基本信息
    """

    @login_required
    @cache.cached(timeout=60)
    def get(self):
        user_id = g.user_id
        try:
            user = User.query.filter_by(uid=user_id).first()
        except:
            return {'code': 500, 'result': 'GetUserResource error'}
        if user:
            return marshal(user, user_fields)
        return {'code': 200, 'result': 'Not find user'}


class PutUserInfo(Resource):
    """
    修改用户信息
    """

    @login_required
    def put(self):
        parser = reqparse.RequestParser()
        args_list = ['user_name', 'like_count', 'email', 'introduction', 'fans_count']
        for args in args_list:
            # 添加校验参数
            parser.add_argument(args)
        parser.add_argument('profile_photo', location='files')
        args = parser.parse_args()
        user_id = g.user_id
        user = User.query.filter_by(uid=user_id)
        if not user:
            return {'code': 500, 'result': 'Server exception!'}

        data = {}
        # 循环参数列表
        for arg in args_list:
            # 获取对应参数的value
            arg_value = args.get(arg)
            # 判断值是否为空，是否需要去更新
            if arg_value:
                # 将需要更新的字段生成字典
                data.update({arg: arg_value})

        user.update(data)
        db.session.commit()
        return {'code': 200, 'data': marshal(user.first(), user_fields)}


def update_recommend_list():
    """
    更新推荐列表  更新到缓存中
    :return:
    """
    try:
        channel_list = Channel.query.all()
        content = {}
        for channel in channel_list:
            channel_id = channel.cid
            # 获取每个频道的资讯    排序 获取点赞最多的资讯
            news = News.query.filter_by(channel_id=channel_id).order_by(News.good_count.desc()).first()
            if news:
                content.update({channel.cname: ''})
        # 缓存  将结果缓存
        cache.set('recommend_list', content, timeout=59 * 60)
        logging.debug('set recommend_list success!')
    except:
        error = traceback.format_exc()
        logging.error('update_recommend_list error:{}'.format(error))


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


class AdminUserNews(Resource):
    """
    封禁用户的文章
    """

    @login_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nid', type=int)
        args = parser.parse_args()
        nid = args.get('nid')
        uid = g.user_id
        user = User.query.get(uid)
        news = News.query.get(nid)
        if user.Administrator == 1:
            if news:
                news.status = 0
                db.session.add(user)
                db.session.commit()
            return {'code': 200, 'msg': 'The information was deleted successfully'}
        return {''}


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


api.add_resource(SMSVerificationCodeResource, '/v1_0/sms/codes')
api.add_resource(AuthorizationResource, '/register_user', endpoint='register_user')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(GetUserInfo, '/get_user_info', endpoint='get_user_info')
api.add_resource(PutUserInfo, '/put_user_info', endpoint='put_user_info')
api.add_resource(RefreshToken, '/refresh_token', endpoint='refresh_token')
api.add_resource(AdminStart, '/add_admin_user')
api.add_resource(AdminUserNews, '/new_put')
api.add_resource(UserStatus, '/user_status')
api.add_resource(NewsStatus, '/new_status')
