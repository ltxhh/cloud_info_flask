from flask import g
from functools import wraps


def login_required(func):
    """
        强制登录的装饰器
        """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user_id is not None:
            return func(*args, **kwargs)
        return {'code': 401, 'message': 'Invalid token account is none'}

    return wrapper
