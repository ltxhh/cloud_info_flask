# -*- codeing = utf-8 -*-
# @Time : 2022/3/14 20:05
# @Author : linyaxuan
# @File : demo.py
# @Software : PyCharm

"""
print('www', 'baidu', 'com', sep='.')  # www.baidu.com

# 九九乘法表
for i in range(1, 10):
    for k in range(1, i+1):
        print("{}*{}={}\t".format(i, k, i * k), end='')
    print()
"""

# https://movie.douban.com/top250


from bs4 import BeautifulSoup
import re
import urllib.request
import urllib.error
import xlwt
import sqlite3
import urllib.parse


# User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)
# Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.2242 SLBChan/11
# data = bytes(urllib.parse.urlencode({'key': "value"}), encoding='utf-8')
# response = urllib.request.urlopen('http://baidu.com', data=data)
# print(response.read().decode('utf8'))

def askUrl(baseUrl):
    headers = {
        "User-Agent":
        r"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/92.0.4515.131 Safari/537.36 SLBrowser/8.0.0.2242 SLBChan/11"

    }
    data = bytes(urllib.parse.urlencode({'key': "value"}), encoding='utf-8')
    req = urllib.request.Request(url=baseUrl, data=data, headers=headers)
    response = urllib.request.urlopen(req)
    print(response.status)
    # 获取头部信息
    print(response.getheaders())
    print(response.read().decode('utf8'))


askUrl('https://douban.com')
