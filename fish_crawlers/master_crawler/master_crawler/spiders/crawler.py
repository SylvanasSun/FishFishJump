# -*- coding: utf-8 -*-
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule

from scrapy_redis.spiders import RedisCrawlSpider


class FeedUrlsCrawler(RedisCrawlSpider):
    """
    Crawl link from 'http://dmoztools.net/' and will be put it to the redis queue.
    """

    name = 'dmoz_crawler'
    redis_key = 'dmoz_crawler:start_urls'
    # target_redis_key is key of the should put a link to the redis queue.
    target_redis_key = 'simple_fish_crawler:start_urls'

    rules = (
        Rule(LxmlLinkExtractor(
            restrict_css=('.top-cat', '.sub-cat', '.cat_item')
        ), callback='parse_sites', follow=True),
    )

    def parse_sites(self, response):
        for div in response.css('.title-and-desc'):
            yield {
                'links': div.css('a::attr(href)').extract()
            }
