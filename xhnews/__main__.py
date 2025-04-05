# -*- coding: utf-8 -*-
from __future__ import annotations

import typing as ty  # noqa: F401

import queue
import time
from concurrent.futures import ThreadPoolExecutor
from .app import XHNewsRequest


def fetch(r: XHNewsRequest, out: queue.Queue,
          link: str, title: str = None):
    news = r.get_news(link, title)
    out.put(news)


def main():
    pool = ThreadPoolExecutor(max_workers=10)

    r = XHNewsRequest()
    focus = r.get_today_focus()

    results = queue.Queue()

    for title, link in focus:
        pool.submit(fetch, r, results, link, title)

    failure = 0

    while failure < 3:
        try:
            news = results.get(block=True, timeout=2*failure)
        except queue.Empty:
            failure += 1
            print("... waiting for news... %s" % failure)
            continue

        x = '[%(dt)s] %(title)s %(interviewer)s %(content)s' % dict(
            dt=news.published_at.strftime('%Y-%m-%d %H:%M'),
            title=news.title,
            interviewer=news.interviewer,
            content=news.content[:20] + '...'
        )
        print(x)

    print("... done ...")


if __name__ == '__main__':
    main()
