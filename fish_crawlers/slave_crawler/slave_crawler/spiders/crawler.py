# -*- coding: utf-8 -*-
import time

from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider

from fish_core.scrapy.items import CommonItem
from fish_core.simhash import Simhash


class SimpleCrawler(RedisCrawlSpider):
    """
    A simple example for distributed crawler,
    it would extract the attribute from a page such as title, description, keywords....
    """

    name = 'simple_fish_crawler'
    redis_key = 'simple_fish_crawler:start_urls'

    rules = (
        Rule(LxmlLinkExtractor(), callback='parse_page', follow=True),
    )

    def parse_page(self, response):
        self.logger.debug('Parse function called on %s ' % response.url)
        item = CommonItem()
        item['title'] = ''.join(response.xpath('//title/text()').extract())
        item['description'] = ''.join(response.xpath('//meta[contains(@name,"description")]/@content').extract())
        item['keywords'] = ''.join(response.xpath('//meta[contains(@name,"keywords")]/@content').extract())
        item['p_texts'] = response.xpath('//p/text()').extract()
        item['url'] = response.url
        item['crawled_timestamp'] = time.time()
        item['links'], item['links_text'] = self.parse_links(response.xpath('//a[contains(@href,"http")]'))
        item['simhash'] = self.generate_simhash(item)
        self.logger.debug('Parse done...........')
        return item

    def parse_links(self, a_list):
        links, links_text = [], []
        for a in a_list:
            links.append(''.join(a.xpath('@href').extract()))
            links_text.append(''.join(a.xpath('text()').extract()))
        return links, links_text

    def generate_simhash(self, item):
        """
        Generate simhash based on title, description, keywords, p_texts and links_text.
        """
        list = item['p_texts'] + item['links_text']
        list.append(item['title'])
        list.append(item['description'])
        list.append(item['keywords'])
        return Simhash(','.join(list).strip()).hash
