# -*- codeing = utf-8 -*-
# @Author : linyaxuan
# @File : new_task.py
# @Software : PyCharm


import time
import logging
import traceback
from flask_restful import marshal, fields

from common.models.models import News, Channel

news_fields = {
    'nid': fields.Integer,
    'user_id': fields.Integer,
    'channel_id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'good_count': fields.Integer
}


def update_recommend_list(cache, flask_app):
    """
    更新推荐列表  更新到缓存中
    :return:
    """
    try:
        with flask_app.app_context():
            channel_list = Channel.query.all()
            content = {}
            for channel in channel_list:
                channel_id = channel.cid
                # 获取每个频道的资讯    排序 获取点赞最多的资讯
                news = News.query.filter_by(channel_id=channel_id).order_by(News.good_count.desc()).first()
                if news:
                    content.update({channel.cname: marshal(news, news_fields)})
            # 缓存  将结果缓存
            cache.set('recommend_list', content, timeout=60 * 5)
            logging.debug('set recommend_list success!')
    except:
        error = traceback.format_exc()
        logging.error('update_recommend_list error:{}'.format(error))
