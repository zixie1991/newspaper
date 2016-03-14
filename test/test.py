#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
import time

import requests
from newspaper import Article


def test():
    url = 'http://blog.csdn.net/kongqz/article/details/50243443'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)
    t = time.time()
    a = Article(url, language='zh', keep_article_html=True)
    print time.time() - t
    a.parse(url=url, html=r.text)

    print time.time() - t

    print a.title
    print a.top_img
    print a.imgs
    # print a.text
    # print a.article_html
    print a.is_valid_body()

if __name__ == '__main__':
    test()
