from flask import g
from functools import wraps


def login_required(func):
    """
        强制登录的装饰器
        """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.account is not None:
            print('111111',func)
            return func(*args, **kwargs)
        return {'code': 401, 'message': 'Invalid token account is none'}

    return wrapper
