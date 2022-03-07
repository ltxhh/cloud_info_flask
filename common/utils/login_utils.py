from flask import g
from functools import wraps


# 强制登陆装饰器的实现
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user_id is not None:
            return func(*args, **kwargs)
        else:
            return {'msg': 'Invalid token'}, 401

    return wrapper
