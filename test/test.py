#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
import time

import requests
from newspaper import Article

from bs4 import BeautifulSoup
import chardet
import six
import hashlib
import re

def to_unicode(text):
    '''文本转unicode(utf-8)
    '''
    encoding = None
    try:
        encoding = chardet.detect(text)['encoding']
    except:
        pass

    if not encoding:
        encoding = 'utf-8'
    encoding = encoding.lower()

    try:
        if isinstance(text, str):
            text = text.decode(encoding)
        else:
            text = text.encode(encoding).decode('utf-8')
    except Exception, e:
        if isinstance(text, str):
            try:
                text = text.decode('gbk')
            except Exception, e:
                text = text.decode('gb2312')
        else:
            try:
                text = text.encode('gbk').decode('utf-8')
            except:
                text = text.encode('gb2312').decode('utf-8')
    except Exception, e:
        print '文本转unicode(utf-8)', e

    return text

def test():
    url = sys.argv[1]
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)
    t = time.time()
    a = Article(url, language='zh', keep_article_html=True)
    print time.time() - t
    html = to_unicode(r.content)
    a.parse(url=url, html=html)

    print time.time() - t

    print a.title
    print a.top_img
    print a.imgs
    print a.text
    # print a.article_html
    print a.is_valid_body()

if __name__ == '__main__':
    test()
