# -*- coding: utf-8 -*-

import datetime
import re
import urlparse

import scrapy
from scrapy.exceptions import CloseSpider

from .base import BaseSpider
from ..items import Link, Loader


FG_URLS = [
    'http://www.fangraphs.com/blogs/',
    'http://www.fangraphs.com/community/',
    'http://www.fangraphs.com/plus/',
]

DATE_RE = re.compile(
    r'((?:January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,2}, [0-9]{4})'
)

class FangraphsSpider(BaseSpider):
    name = 'fangraphs'
    allowed_domains = ['fangraphs.com']
    start_urls = ('http://www.fangraphs.com/blogs/wp-login.php', )

    def parse(self, response):
        """Creates authenticated Fangraphs session"""

        username = self.settings.get('FG_USERNAME')
        password = self.settings.get('FG_PASSWORD')

        if not (username and password):
            raise CloseSpider(reason='Please provide your Fangraphs login '
                                     'via `FG_USERNAME` and `FG_PASSWORD` '
                                     'settings.')

        yield scrapy.FormRequest.from_response(
            response,
            formdata={'log': username,
                      'pwd': password,
                      'rememberme': 'forever',
                      'wp-submit': 'Log In',
                      'redirect_to': 'http://www.fangraphs.com/index.aspx',
                      'testcookie': '1'},
            callback=self.post_login)

    def post_login(self, response):        
        bits = urlparse.urlparse(response.url)

        if '/blogs/wp-login.php' in bits.path:
            self.logger.warning( response.body )
            raise CloseSpider(reason='Fangraphs login failed. '
                                     'Please check your credentials and '
                                     'try again.')

        # authentication successful, crawl on
        for url in FG_URLS:
            yield scrapy.Request(url, callback=self.parse_list_pages)

    def parse_list_pages(self, response):
        links = response.css('#blogcontent .post h2.posttitle a::attr(href)')

        for link in links.extract():
            url = urlparse.urljoin(response.url, link)
            self.logger.debug('Requesting article URL: {}'.format(url))
            yield scrapy.Request(url, callback=self.extract_links_from_source)

        # find next page
        pagination_href = (
            response.xpath('//a[contains(., "Next Page")]/@href')
            .extract_first())

        # continue to next page if possible
        if pagination_href:
            url = urlparse.urljoin(response.url, pagination_href)
            self.logger.debug('Requesting next article list URL: ' + url)
            yield scrapy.Request(url, callback=self.parse_list_pages)

    def extract_links_from_source(self, response):
        """Extracts links from an article page,
        then spawns extraction of all links found.
        """

        paywalled = (
            response.xpath(
                '//div[@class="fullpostentry" and contains(., "to read the rest of this post or")]'
            )
            .extract_first())

        if paywalled:
            raise CloseSpider(reason='Paywall not broken. Check your '
                                     'Fangraphs credentials and try again.\n'
                                     '\t{}'.format(response.url))

        return super(FangraphsSpider, self).extract_links_from_source(response)

    def get_article_links(self, selector):
        return selector.css('.fullpostentry a::attr(href)').extract()

    def get_publisher_code(self):
        return self.settings['P_FG']

    def get_pub_date(self, response):
        value = response.css('div.post p.postmeta::text').extract_first()
        value = value.strip()

        value = DATE_RE.search(value)

        if value is not None:
            value = datetime.datetime.strptime(value.group(1), '%B %d, %Y')
            return value.strftime('%Y-%m-%d')

        return None

        # links = response.css()

        # for link in links.extract():
        #     dest_url = urlparse.urljoin(response.url, link)

        #     for pattern in settings.IGNORE:
        #         if pattern.search(dest_url) is not None:
        #             self.logger.debug('Skipping blacklisted URL: '
        #                               + dest_url)
        #             break
        #     else:
        #         self.logger.info('Found relationship: ' + dest_url)

        #         # emit relationship
        #         yield Link(src_url=response.url, dest_url=dest_url)
