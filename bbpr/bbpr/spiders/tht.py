# -*- coding: utf-8 -*-

"""Extracts links from Hardball Times and THT Live posts.
"""

import datetime
import urlparse

import scrapy

import urltools

from .base import BaseSpider
from ..items import Link, Loader


class HardballTimesSpider(BaseSpider):
    name = 'tht'
    allowed_domains = ('thehardballtimes.com', 'hardballtimes.com', )
    start_urls = (
        'http://www.hardballtimes.com/articles/',
        'http://www.hardballtimes.com/tht-live/',
    )

    def parse(self, response):
        # find links in list
        links = response.css('article.post h1.entry-title a::attr(href)')

        for href in links.extract():
            url = urlparse.urljoin(response.url, href)
            self.logger.debug('Requesting article URL: {}'.format(url))
            yield scrapy.Request(url, callback=self.extract_links_from_source)

        # respawn if pagination controls are present
        pagination_href = (response.css('li.pagination-next a::attr(href)')
                           .extract_first())

        if pagination_href:
            url = urlparse.urljoin(response.url, pagination_href)
            self.logger.info('Requesting next article list URL: ' + url)
            yield scrapy.Request(url, callback=self.parse)

    def get_article_links(self, selector):
        return (selector.css('article.post div.entry-content a::attr(href)')
                .extract())

    def get_publisher_code(self):
        return self.settings['P_THT']

    def get_pub_date(self, response):
        pub_date = (response.css('time.entry-time::attr(datetime)')
                    .extract_first())
        pub_date = datetime.datetime.strptime(pub_date,
                                              '%Y-%m-%dT%H:%M:%S+00:00')
        return pub_date.strftime('%Y-%m-%d')
