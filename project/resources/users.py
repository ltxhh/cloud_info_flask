from common.models.users import User, db
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal, fields
import traceback
user_bp = Blueprint('users', __name__)
api = Api(user_bp)

# 定义序列化字段

user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'age': fields.Integer
}


# 添加用户
class AddUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            lis = ['name', 'age']
            for i in lis:
                parser.add_argument(i, location='form')
            args = parser.parse_args()
            user = User()
            user.name = args.get('name')
            user.age = args.get('age')
            db.session.add(user)
            db.commint()
            return '添加成功'
        except:
            error = traceback.format_exc()
            print(error)
            return 'error'


api.add_resource(AddUser, '/addUser')
