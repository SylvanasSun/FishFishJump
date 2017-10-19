# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FishCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    url = scrapy.Field()
    links = scrapy.Field()
    link_texts = scrapy.Field()  # Text content in each tag <a>
