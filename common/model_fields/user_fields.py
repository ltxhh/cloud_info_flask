# -*- codeing = utf-8 -*-
# @Time : 2022/3/28 9:22
# @Author : linyaxuan
# @File : user_fields.py
# @Software : PyCharm

from common.models.models import User

from flask_restful import fields

user_fields = {
    'uid': fields.Integer,
    'account': fields.String,
    'password': fields.String,
    'mobile': fields.String
}
