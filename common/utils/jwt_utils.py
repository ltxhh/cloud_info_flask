# 创建Token与校验Token


import jwt
from flask import current_app, g
from datetime import datetime, timedelta


def generate_jwt(payload, expiry, secret=None):
    """"
    生成jwt
     payload: dict 载荷
     expiry: datetime 有效期
     secret: 盐
    :return: token
    """
    _payload = {
        'exp': expiry
    }
    _payload.update(payload)

    if not secret:
        secret = current_app.config['JWT_SECRET']

    token = jwt.encode(_payload, secret, algorithm='HS256')

    return token


def verify_jwt(token, secret=None):
    """
    校验jwt
    :param token: token值
    :param secret: 盐
    :return: payload 载荷
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithms='HS256')
    except:
        payload = None
    return payload


# 更新token
def _generate_token(user_id, refresh=True):
    """
    生成token
    :param user_id:
    """
    # 获取盐
    secret = current_app.config.get('JWT_SECRET')
    # 定义过期时间
    expiry = datetime.utcnow() + timedelta(hours=2)
    # 生成Token
    token = 'Bearer ' + generate_jwt({'user_id': user_id}, expiry, secret)
    if refresh:
        expiry = datetime.utcnow() + timedelta(days=15)
        # is_refresh作为更新token的信号
        refresh_token = 'Bearer ' + generate_jwt({'user_id': user_id, 'is_refresh': True}, expiry, secret)
    else:
        refresh_token = None
    return token, refresh_token


def refresh_token():
    """
    刷新token
    :return:
    """
    if g.user_id is not None and g.is_refresh is True:
        token, refresh_token = _generate_token(g.user_id, refresh=False)
        return {'message': 'ok', 'data': {'token': token}}
    else:
        return {'message': 'Invalid refresh token', 'code': 403}
