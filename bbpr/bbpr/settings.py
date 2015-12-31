# -*- coding: utf-8 -*-

BOT_NAME = 'bbpr'

SPIDER_MODULES = ['bbpr.spiders']
NEWSPIDER_MODULE = 'bbpr.spiders'

L_DIRECT = 'direct'
L_RELATED = 'related'
L_TERTIARY = 'tertiary'

# publisher codes
P_FG = 'fg'
P_BPRO = 'bpro'
P_THT = 'tht'

USER_AGENT = 'bbpr (+http://github.com/mattdennewitz/baseball-pagerank)'

CONCURRENT_REQUESTS = 16

COOKIES_ENABLED = True
COOKIES_DEBUG = True

try:
    from local_settings import *
except ImportError:
    pass
