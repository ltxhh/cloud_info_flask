# -*- codeing = utf-8 -*-
# @Author : linyaxuan
# @File : custom_output_json.py
# @Software : PyCharm

import json

from flask import current_app, make_response


def custom_output_json(data, code, headers=None):
    # 定制JSON格式
    # 注意: 由于返回错误响应是, 已经在响应数据中包含message, 所以不必要再进行定制了, 所以进行了if判断
    if 'message' not in data:
        data = {
            'message': 'ok',
            'data': data
        }

    settings = current_app.config.get('RESTFUL_JSON', {})

    if current_app.debug:
        settings.setdefault('indent', 4)
        settings.setdefault('sort_keys')

    dumped = json.dumps(data, **settings) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp