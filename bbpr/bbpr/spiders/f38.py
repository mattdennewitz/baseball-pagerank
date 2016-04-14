# -*- coding: utf-8 -*-

"""Extracts links from Hardball Times and THT Live posts.
"""

import datetime
import urlparse

import scrapy

import urltools

from .base import BaseSpider
from ..items import Link, Loader


class F38(BaseSpider):
    name = 'f38'
    allowed_domains = ('fivethirtyeight.com', 'www.fivethirtyeight.com')
    start_urls = (
        'http://fivethirtyeight.com/tag/baseball/',
    )

    def parse(self, response):
        # find links in list
        links = response.css('h2.article-title a::attr(href)')

        self.logger.info('Found %s links', len(links))

        for href in links.extract():
            url = urlparse.urljoin(response.url, href)
            self.logger.debug('Requesting article URL: {}'.format(url))
            yield scrapy.Request(url, callback=self.extract_links_from_source)

        # respawn if pagination controls are present
        pagination_href = (response.css('a.link-sectionmore:not(.sectionprevious)::attr(href)')
                           .extract_first())

        if pagination_href:
            url = urlparse.urljoin(response.url, pagination_href)
            self.logger.info('Requesting next article list URL: ' + url)
            yield scrapy.Request(url, callback=self.parse)

    def get_article_links(self, selector):
        return (selector.css('div.entry-content a::attr(href)')
                .extract())

    def get_publisher_code(self):
        return self.settings['P_538']

    def get_pub_date(self, response):
        pub_date = (response.css('span.datetime.updated::attr(title)')
                    .extract_first())
        pub_date = datetime.datetime.strptime(pub_date,
                                              '%Y-%m-%dT%H:%M:%S+00:00')
        return pub_date.strftime('%Y-%m-%d')
