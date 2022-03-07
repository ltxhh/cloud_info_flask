# 数据库连接配置


class sqlconfig(object):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:linyaxuan666@127.0.0.1:3306/cloud_info_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JWT_SECRET = 'LSJFLSJFLWE23O9UDFNSDF'
    # CACHE_REDIS_HOST = '127.0.0.1',
    # CACHE_REDIS_PORT = 6379,
    # CACHE_REDIS_DB = 6,
    # CACHE_REDIS_PASSWORD = ''


import redis
import pickle


# redis 的配置
class Redis:
    @staticmethod
    def connect():
        r = redis.StrictRedis(host='127.0.0.1', port=6379)
        return r

    # 将内存数据二进制通过序列号转为文本流，再存入redis
    @staticmethod
    def set_data(r, key, data, ex=None):
        r.set(key, pickle.dumps(data), ex)

    # 将文本流从redis中读取并反序列化，返回返回
    @staticmethod
    def get_data(r, key):
        data = r.get(key)
        if data is None:
            return None
        return pickle.loads(data)
