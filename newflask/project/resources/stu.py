from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from common.models.stu import Stu, Sub, db
from flask_restful import Resource, marshal, fields
import traceback

stu = Blueprint('stu', __name__)
api = Api(stu)

# 定义序列化字段
stu_fields = {
    'id': fields.Integer,
    'name': fields.String
}
sub_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'age': fields.Integer,
    'snum': fields.Integer,
    'sub_id': fields.Integer,
}


# 添加 Sbu
class AddSub(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='form')
        args = parser.parse_args()
        sub = Sub()
        sub.name = args.get('name')
        db.session.add(sub)
        db.session.commit()
        return '添加成功!'


# 添加 Sbu
class AddStu(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        lis = {'name', 'age', 'snum', 'sub_id'}
        for k in lis:
            parser.add_argument(k, location='form')
        args = parser.parse_args()
        stu = Stu()
        stu.name = args.get('name')
        stu.age = args.get('age')
        stu.snum = args.get('snum')
        stu.sub_id = args.get('sub_id')
        db.session.add(stu)
        db.session.commit()
        return '添加成功!'


# 更新 Sub信息
class UpSub(Resource):
    def put(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=int, location='args')
            parser.add_argument('name', type=str, location='form')
            args = parser.parse_args()
            id = args.get('id')
            name = args.get('name')
            Sub.query.filter_by(id=id).update({'name': name})
            db.session.commit()
            return '修改成功'
        except:
            error = traceback.format_exc()
            print(error)
            return 'error'


# 删除 Sub信息
class DelSub(Resource):
    def delete(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=int, location='args')
            args = parser.parse_args()
            id = args.get('id')
            print('111111', id)
            Stu.query.filter_by(sub_id=id).delete()
            # db.session.commit()
            Sub.query.filter_by(id=id).delete()
            db.session.commit()
            return '删除成功'
        except:
            error = traceback.format_exc()
            print(error)
            return 'error'


api.add_resource(AddSub, '/addSub', endpoint='sub')
api.add_resource(AddStu, '/addStu')
api.add_resource(UpSub, '/upSub')
api.add_resource(DelSub, '/delSub')
