# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class Loader(ItemLoader):
    default_output_processor = TakeFirst()


class Link(scrapy.Item):
    publisher = scrapy.Field()
    pub_date = scrapy.Field()
    src_url = scrapy.Field()
    dest_url = scrapy.Field()


# - stash loading bpro page values -
# loader.add_value('publisher', 'bpro')
# loader.add_css('title', 'h1.title::text')
# loader.add_css('subhead', 'h2.subhead::text')
# loader.add_css('author', 'p.author a.author::text')
# loader.add_css('pub_date', 'p.date::text')
# loader.add_value('dest_url', response.url)
# loader.add_value('dest_url')
