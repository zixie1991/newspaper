# -*- coding: utf-8 -*-
__title__ = 'newspaper'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import logging
import re

from .configuration import Configuration
from .extractors import ContentExtractor
from .outputformatters import OutputFormatter
from .utils import extend_config

log = logging.getLogger(__name__)


class ArticleException(Exception):
    pass


class Article(object):
    """Article objects abstract an online news article page
    """
    def __init__(self, url, config=None, **kwargs):
        """The **kwargs argument may be filled with config values, which
        is added into the config object
        """
        self.config = config or Configuration()
        self.config = extend_config(self.config, kwargs)

        self.extractor = ContentExtractor(self.config)

    def __init(self, url):
        self.url = url
        self.title = ''

        # URL of the "best image" to represent this article
        self.top_img = self.top_image = u''

        # All image urls in this article
        self.imgs = self.images = []

        # Body text from this article
        self.text = u''

        # This article's unchanged and raw HTML
        self.html = u''

        # The HTML of this article's main node (most important part)
        self.article_html = u''

        # Holds the top element of the DOM that we determine is a candidate
        # for the main body of the article
        self.top_node = None

        # lxml DOM object generated from HTML
        self.doc = None

    def parse(self, url=None, html=None):
        self.__init(url)
        self.set_html(html)
        self.doc = self.config.get_parser().fromstring(self.html)

        self.remove_advertisement(self.doc)

        if self.doc is None:
            # `parse` call failed, return nothing
            return

        output_formatter = OutputFormatter(self.config)

        title = self.extractor.get_title(self.doc)
        self.set_title(title)

        text = u''
        self.top_node = self.extractor.calculate_best_node(self.doc)
        if self.top_node is not None:

            first_img = self.extractor.get_first_img_url(
                self.url, self.top_node)
            self.set_top_img(first_img)

            imgs = self.extractor.get_img_urls(self.url, self.top_node)
            self.set_imgs(imgs)

            self.top_node = self.extractor.post_cleanup(self.top_node)
            text, article_html = output_formatter.get_formatted(
                self.top_node)
            self.set_article_html(article_html)
            self.set_text(text)

    def is_valid_body(self):
        """If the article's body text is long enough to meet
        standard article requirements, keep the article
        """
        # 混合字串统计
        re_zh = re.compile(u'[\u1100-\uFFFDh]+?')
        wordcount = re_zh.sub(' a ', self.text).split(' ')  # replace the zh with the word a
        sentcount = re.split('.|。', self.text)

        if len(wordcount) > (self.config.MIN_WORD_COUNT):
            log.debug('%s verified for article and wc' % self.url)
            return True

        if self.title is None or len(self.title.split(' ')) < 2:
            log.debug('%s caught for bad title' % self.url)
            return False

        if len(wordcount) < self.config.MIN_WORD_COUNT:
            log.debug('%s caught for word cnt' % self.url)
            return False

        if len(sentcount) < self.config.MIN_SENT_COUNT:
            log.debug('%s caught for sent cnt' % self.url)
            return False

        if self.html is None or self.html == u'':
            log.debug('%s caught for no html' % self.url)
            return False

        log.debug('%s verified for default true' % self.url)
        return True

    def set_title(self, title):
        if self.title and not title:
            # Title has already been set by an educated guess and
            # <title> extraction failed
            return
        title = title[:self.config.MAX_TITLE]
        self.title = title

    def set_text(self, text):
        text = text[:self.config.MAX_TEXT]
        self.text = text

    def set_html(self, html):
        """Encode HTML before setting it
        """
        self.html = html

    def set_article_html(self, article_html):
        """Sets the HTML of just the article's `top_node`
        """
        self.article_html = article_html

    def set_top_img(self, src_url):
        self.top_img = self.top_image = src_url

    def set_imgs(self, imgs):
        """The motive for this method is the same as above, provide APIs
        for both `article.imgs` and `article.images`
        """
        self.images = imgs
        self.imgs = imgs

    def remove_advertisement(self, node):
        '''
        广告或推广链接
        <p><a href="">a</a></p>
        <p><a href="">b</a></p>
        <p><a href="">c</a></p>
        '''
        for tag in self.config.get_parser().xpath_re(node, '//p/a'):
            tag.getparent().remove(tag)

        '''
        <ul>
            <li><a href="">a</a></li>
            <li><a href="">b</a></li>
            <li><a href="">c</a></li>
        </ul>
        '''
        for tag in self.config.get_parser().xpath_re(node, '//li/a'):
            tag.getparent().remove(tag)

        for tag in self.config.get_parser().xpath_re(node, '//td/a'):
            tag.getparent().remove(tag)
