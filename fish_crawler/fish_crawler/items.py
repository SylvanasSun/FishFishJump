# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommonItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    p_texts = scrapy.Field()  # Text content in each tag <p>
    url = scrapy.Field()
    date = scrapy.Field()  # Current page date,general get from Last-Modified in the response
    links = scrapy.Field()
    link_texts = scrapy.Field()  # Text content in each tag <a>
    simhash = scrapy.Field()  # Simhash code,depend title,description,keywords,p_texts and link_texts
