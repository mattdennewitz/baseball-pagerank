# -*- coding: utf-8 -*-

BOT_NAME = 'bbpr'

SPIDER_MODULES = ['bbpr.spiders']
NEWSPIDER_MODULE = 'bbpr.spiders'

# publisher codes
P_FG = 'fg'
P_BPRO = 'bpro'
P_THT = 'tht'

USER_AGENT = 'bbpr (+http://github.com/mattdennewitz/baseball-pagerank)'

CONCURRENT_REQUESTS = 16

COOKIES_ENABLED=False

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_MAX_DELAY = 60

HTTPCACHE_ENABLED=True
HTTPCACHE_EXPIRATION_SECS=0
HTTPCACHE_DIR='httpcache'
HTTPCACHE_IGNORE_HTTP_CODES=[]
HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
