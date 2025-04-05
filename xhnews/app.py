# -*- coding: utf-8 -*-
from __future__ import annotations

import typing as ty  # noqa: F401
import re
import datetime
import requests
import dataclasses
from bs4 import BeautifulSoup


@dataclasses.dataclass
class XHNews:
    title: str
    link: str
    published_at: datetime.datetime | None = None
    interviewer: str | None = None
    content: str | None = None


class XHNewsRequest(object):
    XH_ENTRY = 'https://www.news.cn/'

    INTERVIEWER_PATTERN = re.compile(r'记者[\s﻿]?(?P<interviewer>[\u4eff-\u9fa5、]+)[\s）]?')

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_today_focus(self) -> ty.List[ty.Tuple[str, str]]:
        """
        获取今日头条
        :return: 今日头条标题和链接
        """
        response = self.session.get(self.XH_ENTRY)
        soup = BeautifulSoup(response.text, 'lxml')

        focus = soup.find(id='depth')

        items = focus.find_all('li')

        if not items:
            return list()

        output = list()
        for item in items:
            link_ = item.find('a')
            title = link_.text.strip()
            link = link_['href']
            output.append((title, link))

        return output

    @staticmethod
    def parse_news_published_date(s: BeautifulSoup) -> datetime.datetime | None:
        try:
            container = s.find("div", class_="header-time")
        except IndexError:
            return None

        year = container.find("span", class_="year").text.strip()
        month_day = container.find("span", class_="day").text.strip()
        time_ = container.find("span", class_="time").text.strip()

        dt = '%s/%s %s' % (year, month_day, time_)
        dt = datetime.datetime.strptime(dt, '%Y/%m/%d %H:%M:%S')

        return dt

    @staticmethod
    def parse_news_title(s: BeautifulSoup) -> str | None:
        container = s.find("div", class_="head-line")
        title = container.find('h1').text.strip()
        return title

    @staticmethod
    def parse_news_content(s: BeautifulSoup) -> str | None:
        container = s.find("div", attrs={"id": "detail"})
        parts = container.find_all('p')

        lines = list()

        for part in parts:
            lines.append(part.text.strip())

        content = '\n'.join(lines)
        return content

    def get_news(self, link: str, title: str = None) -> XHNews:
        """
        获取新闻详情
        :param link: 新闻链接
        :param title: 新闻标题
        :return: 新闻详情
        """
        response = self.session.get(link)
        soup = BeautifulSoup(response.text, 'lxml')

        if title is None:
            title = self.parse_news_title(soup)

        published_at = self.parse_news_published_date(soup)

        content = self.parse_news_content(soup)
        m = self.INTERVIEWER_PATTERN.search(content)
        if m:
            interviewer = m.groupdict()['interviewer']
        else:
            interviewer = None

        news = XHNews(
            title=title,
            link=link,
            published_at=published_at,
            interviewer=interviewer,
            content=content,
        )

        return news
