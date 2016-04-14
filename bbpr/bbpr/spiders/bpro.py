# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re
import urlparse

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader

from ..items import Link


def should_follow(url):
    bits = urlparse.urlparse(url)
    if bits.hostname in ('baseballprospectus.com',
                         'www.baseballprospectus.com'):
        # limit only to /article.php
        return ((bits.path.startswith('/a/')
                or bits.path.startswith('/article.php')))

    return True


def normalize_url(url):
    """Cleans up a BPro URL
    """

    bits = urlparse.urlparse(url, allow_fragments=False)
    bits = list(bits)

    # clean up query string
    qs = urlparse.parse_qs(bits[4])

    # normalize article links
    if '/article.php' in bits[2]:
        qs = dict(filter(lambda (k, v): k == 'articleid', qs.items()))

    # revert /a/ links to article.php links
    elif '/a/' in bits[2]:
        bits[2] = '/article.php'
        qs = {'articleid': [bits[2].split('/')[-1]]}

    qs = '&'.join([
        '{}={}'.format(k, v[0])
        for (k, v)
        in qs.items()
    ])

    bits[4] = qs

    return urlparse.urlunparse(bits)


class BproSpider(scrapy.Spider):
    name = 'bpro'
    allowed_domains = ('baseballprospectus.com', 'google.com', 'bbp.cx', )
    start_urls = (
        'http://www.baseballprospectus.com/articles/',
    )

    def __init__(self, *a, **kw):
        super(BproSpider, self).__init__(*a, **kw)

        self.username = getattr(self.settings, 'BPRO_USERNAME')
        self.password = getattr(self.settings, 'BPRO_PASSWORD')

        if not self.username or not self.password:
            raise CloseSpider(
                'Please set BPRO_USERNAME and BPRO_PASSWORD settings '
                'with valid Baseball Prospectus account credentials')

    def start_requests(self):
        resp = scrapy.FormRequest(
            'http://www.baseballprospectus.com/ajax/session_handler.php',
            formdata={'username': self.username,
                      'password': self.password,
                      'type': 'login',
                      'action': 'muffinklezmer'},
            callback=self.post_login)
        return [resp]

    def post_login(self, response):
        yield scrapy.Request('http://www.baseballprospectus.com/articles/',
                             callback=self.parse)

    def parse(self, response):
        """Extracts links from "All Articles" list.
        Links are then sent to `self.extract_article_links`
        for processing.
        """

        # find links in list
        article_links = (
            response
            .css('.articleHead table tr td:first-of-type a::attr(href)')
            .extract())

        for link in article_links:
            url = urlparse.urljoin(response.url, link)
            url = normalize_url(url)
            yield scrapy.Request(url, callback=self.extract_article_links)

        # respawn if pagination controls are present
        pagination = (
            response
            .xpath('//a[contains(., "Previous Article Entries")]/@href')
            .extract())

        if len(pagination) > 0:
            href = pagination.pop(0)
            url = urlparse.urljoin(response.url, href)
            self.logger.info('Requesting next article list URL: ' + url)
            yield scrapy.Request(url, callback=self.parse)

    def extract_article_links(self, response):
        """Extracts links from an article page, then follows each
        same-domain URL to further link extraction.
        """

        paywalled = (
            response
            .xpath('//h1[contains(., "The rest of this article is '
                   'restricted to Baseball Prospectus Subscribers.")]')
            .extract())

        if len(paywalled) > 0:
            raise StopIteration()

        links = response.css('.article a::attr(href)').extract()

        for link in links:
            dest_url = urlparse.urljoin(response.url, link)

            if not should_follow(dest_url):
                self.logger.warning('Skipping {}'.format(dest_url))
                continue

            dest_url = normalize_url(dest_url)

            for pattern in IGNORE:
                if pattern.search(dest_url) is not None:
                    self.logger.debug('Skipping blacklisted URL: '
                                      + dest_url)
                    break
            else:
                pass
                self.logger.info('Found relationship: ' + dest_url)

                # emit relationship
                yield Link(src_url=response.url, dest_url=dest_url)

                # extract destination page's outbound links
                yield scrapy.Request(dest_url,
                                     callback=self.extract_article_links)
