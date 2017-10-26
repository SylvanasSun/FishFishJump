# -*- coding: utf-8 -*-

# Scrapy settings for fish_crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'fish_crawler'

SPIDER_MODULES = ['fish_crawler.spiders']
NEWSPIDER_MODULE = 'fish_crawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'fish_crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# The maximum running time, the unit is second.
# It is used with main() of in the 'run.py', 82800 second is 23 hours
# and main() of in the 'run.py' every 24 hours will start once crawler 'fish_simple_crawler'.
# You can choose not to set this configuration and no use run.py
# but you can to implements self-defined schedule function of yourself.
CLOSESPIDER_TIMEOUT = 82800

# The two configuration for enhance crawler efficiency on the below.
# By the way you must reference your machines to set them for better efficiency.
CONCURRENT_REQUESTS = 100
REACTOR_THREADPOOL_MAXSIZE = 20

# Cookies for Search Engine crawler is not important so ban it will be bring better efficiency.
COOKIES_ENABLED = False

# Retry HTTP request will bring worse efficiency
# especially when sites causes are very slow (or fail) to respond.
RETRY_ENABLED = False

# Reduce the download timeout so that stuck requests are discarded
# quickly and free up capacity to process the next ones.
DOWNLOAD_TIMEOUT = 15

ITEM_PIPELINES = {
    'fish_crawler.pipelines.DuplicatesPipeline': 200,
    'fish_crawler.pipelines.MongodbPipeline': 300
}

EXTENSIONS = {
    # 'fish_crawler.extensions.SendEmailExtension': 400,
}

# The item pipeline serializes and stores the items in this mongodb collection.
MONGODB_COLLECTION_NAME = '%(spider)s:items'

# The database name of Mongodb.
MONGODB_DB_NAME = '%(spider)s'

# Specify the full Mongodb URL for connecting
# Its priority greater than MONGODB_HOST and MONGODB_PORT
MONGODB_URL = 'mongodb://localhost:27017/'

# Specify the host and port to use when connecting to Mongodb.
# MONGODB_HOST = 'localhost'
# MONGODB_PORT = 27017

LOG_LEVEL = 'INFO'
LOG_FILE = 'fish_crawler.log'

# Sender email to use (From: header) for sending emails.
# MAIL_FROM = 'your email'

# MAIL_TO = ['receiver's email',]

# SMTP host to use for sending emails.
# If your email is proxy so you must write host of the proxy.
# MAIL_HOST = 'localhost'

# SMTP port to use for sending emails.
# If your email is proxy so you must write port of the proxy.
# MAIL_PORT = 25

# User to use for SMTP authentication. If disabled no SMTP authentication will be performed.
# MAIL_USER = ''

# Password to use for SMTP authentication, along with MAIL_USER.
# If your email is proxy so you must apply for the authentication code.
# MAIL_PASS = ''

# Enforce using STARTTLS. STARTTLS is a way to take an existing insecure connection,
# and upgrade it to a secure connection using SSL/TLS.
# MAIL_TLS = False

# Enforce connecting using an SSL encrypted connection
# MAIL_SSL = False

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 1

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Enables scheduling storing requests queue in redis.
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True

# Schedule requests using a priority queue. (default)
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"

# Alternative queues.
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

# Default requests serializer is pickle, but it can be changed to any module
# with loads and dumps functions. Note that pickle is not compatible between
# python versions.
# Caveat: In python 3.x, the serializer must return strings keys and support
# bytes as values. Because of this reason the json or msgpack module will not
# work by default. In python 2.x there is no such issue and you can use
# 'json' or 'msgpack' as serializers.
# SCHEDULER_SERIALIZER = "scrapy_redis.picklecompat"

# Max idle time to prevent the spider from being closed when distributed crawling.
# This only works if queue class is SpiderQueue or SpiderStack,
# and may also block the same time when your spider start at the first time (because the queue is empty).
# SCHEDULER_IDLE_BEFORE_CLOSE = 10

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Specify the full Redis URL for connecting (optional).
# If set, this takes precedence over the REDIS_HOST and REDIS_PORT settings.
# REDIS_URL = 'redis://user:pass@hostname:9001'

# Specify the simhash list for DuplicatesPipeline.
REDIS_SIMHASH_KEY = '%(spider)s:simhash_set'

# Custom redis client parameters (i.e.: socket timeout, etc.)
# REDIS_PARAMS  = {}
# Use custom redis client class.
# REDIS_PARAMS['redis_cls'] = 'myproject.RedisClient'

# If True, it uses redis' ``SPOP`` operation. You have to use the ``SADD``
# command to add URLs to the redis queue. This could be useful if you
# want to avoid duplicates in your start urls list and the order of
# processing does not matter.
# REDIS_START_URLS_AS_SET = False

# Default start urls key for RedisSpider and RedisCrawlSpider.
REDIS_START_URLS_KEY = '%(name)s:start_urls'

# Use other encoding than utf-8 for redis.
# REDIS_ENCODING = 'latin1'
