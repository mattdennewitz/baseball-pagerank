# -*- coding: utf-8 -*-

import datetime
import urlparse

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader

import urltools

from ..items import Link, Loader
from ..patterns import IGNORE


class BaseSpider(scrapy.Spider):
    def parse(self, response):
        raise NotImplementedError(
            'Implement your list page link extraction here')

    def get_article_links(self, selector):
        raise NotImplementedError(
            'Implement your own in-article link extraction here')

    def get_publisher_code(self):
        raise NotImplementedError('Override to define publisher code')

    def get_pub_date(self, response):
        raise NotImplementedError('Override to define pub date extraction')

    def should_scrape(self, src_url, dest_url):
        # ignore anything in our blocklist
        for pattern in IGNORE:
            if pattern.search(dest_url) is not None:
                self.logger.debug('Skipping blacklisted URL: '.format(dest_url))
                return False

        # do not follow same-url links
        if urltools.compare(src_url, dest_url):
            self.logger.debug('Skipping self-link in {}'.format(src_url))
            return False

        return True

    def normalize_url(self, url):
        return urltools.normalize(url.decode('ascii', errors='ignore'))

    def extract_links_from_source(self, response):
        """Extracts links from an article page,
        then spawns extraction of all links found.
        """

        src_url = self.normalize_url(response.url)

        links = self.get_article_links(response)

        self.logger.info('{} has {} urls'.format(src_url, len(links)))

        for href in links:
            dest_url = urlparse.urljoin(src_url, href)
            dest_url = dest_url.encode('ascii', errors='ignore')

            try:
                dest_url = urltools.normalize(dest_url)
            except KeyError:
                if 'mailto' in dest_url:
                    continue
                raise

            # ignore anything specific to this site
            if not self.should_scrape(src_url, dest_url):
                self.logger.debug('Skipping {}: should not scrape'.format(
                                  dest_url))
                continue

            self.logger.info('Found relationship:\n\t{} -> {}'.format(
                             src_url, dest_url))

            # record link pair
            loader = Loader(item=Link(), response=response)
            loader.add_value('publisher', self.get_publisher_code())
            loader.add_value('pub_date', self.get_pub_date(response))
            loader.add_value('src_url', src_url)
            loader.add_value('dest_url', dest_url)

            yield loader.load_item()
