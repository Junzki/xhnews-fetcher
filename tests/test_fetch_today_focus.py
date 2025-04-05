# -*- coding: utf-8 -*-

import typing as ty  # noqa: F401
import unittest
import os
import datetime
import pathlib

import requests
from bs4 import BeautifulSoup
from xhnews.app import XHNewsRequest

CASES_DIR = pathlib.Path(__file__).parent / 'cases'


class TestFetchTodayFocus(unittest.TestCase):

    def setUp(self) -> None:
        self.xh = XHNewsRequest()
        self.news_detail_case = CASES_DIR / 'news-detail-case.html'

        if not os.path.exists(self.news_detail_case):
            self.init_news_detail_case()

    def init_news_detail_case(self):
        link = "https://www.news.cn/legal/20250405/be7da4b1b6e444d498fe196e99c78200/c.html"
        res = requests.get(link)
        res.raise_for_status()

        with open(self.news_detail_case, 'w', encoding='utf-8') as f:
            f.write(res.text)

    def test_get_today_focus(self):
        """
        测试获取今日头条
        :return:
        """
        from xhnews.app import XHNewsRequest

        xh = XHNewsRequest()
        result = xh.get_today_focus()

    def test_parse_date(self):
        """
        测试获取新闻
        :return:
        """
        with open(self.news_detail_case) as f:
            case_ = f.read()

        soup = BeautifulSoup(case_, 'lxml')

        dt = XHNewsRequest.parse_news_published_date(soup)
        self.assertEqual(dt, datetime.datetime(2025, 4, 5, 9, 31, 15))

    def test_parse_title(self):
        """
        测试获取新闻
        :return:
        """
        with open(self.news_detail_case) as f:
            case_ = f.read()

        soup = BeautifulSoup(case_, 'lxml')

        title = XHNewsRequest.parse_news_title(soup)
        self.assertEqual(title, '38项措施让公证服务更便利！司法部部署开展“公证规范优质”行动')

    def test_parse_content(self):
        """
        测试获取新闻
        :return:
        """
        with open(self.news_detail_case) as f:
            case_ = f.read()

        soup = BeautifulSoup(case_, 'lxml')

        content = XHNewsRequest.parse_news_content(soup)
        self.assertTrue(content.startswith('怎样持续提升公证服务质量和公信力？'
                                           '如何让人民群众切实感受到公证法律服务的便捷、高效和优质？'))
        self.assertTrue(content.endswith('积极参与预防化解矛盾纠纷——推动开展公证参与调解工作试点，推进公证服务进村（社区）。'
                                         '（记者齐琪）'))
        self.assertEqual(10, len(content.split('\n')))
