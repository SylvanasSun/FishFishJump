import time

from fish_crawler.items import CommonItem
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.spiders import Rule

from fish_utils.simhash import Simhash
from scrapy_redis.spiders import RedisCrawlSpider


class SimpleCrawler(RedisCrawlSpider):
    """
    Simple Crawler that reads urls from redis queue and crawl all page.
    """
    name = "fish_simple_crawler"

    rules = (
        Rule(LxmlLinkExtractor(), callback='parse_page', follow=True)
    )

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(SimpleCrawler, self).__init__(*args, **kwargs)

    def parse_page(self, response):
        item = CommonItem()
        item['title'] = response.xpath('//title/text()').extract()
        item['description'] = response.xpath('//meta[contains(@name,"description")]/@content').extract()
        item['keywords'] = response.xpath('//meta[contains(@name,"keywords")]/@content').extract()
        item['p_texts'] = response.xpath('//p/text()').extract()
        item['url'] = response.url
        item['crawled_timestamp'] = time.time()
        item['links'] = self.parse_links(response.xpath('//a[contains(@href,"http")]'))
        item['simhash'] = self.generate_simhash(item)
        return item

    def parse_links(self, a_list):
        """
        Parse list of tag a then packing to a list(like [['example.com','example text'],....]).
        """
        result = []
        for a in a_list:
            list = [a.xpath('@href').extract(), a.xpath('text()').extract()]
            result.append(list)
        return result

    def generate_simhash(self, item):
        """
        Generate simhash based on title, description, keywords, p_texts and link text.
        """
        list = item['title'] + item['description'] + item['keywords'] + item['p_texts']
        for link in item['links']:
            list.append(link[1])
        return Simhash(','.join(list).strip()).hash
