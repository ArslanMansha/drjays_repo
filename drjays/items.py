# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DrjaysCodeItem(scrapy.Item):
    product_id = scrapy.Field()
    name = scrapy.Field()
    maker = scrapy.Field()
    category = scrapy.Field()
    collection = scrapy.Field()
    pricing = scrapy.Field()
    available_sizes = scrapy.Field()
    description = scrapy.Field()
    fabric = scrapy.Field()
    color = scrapy.Field()
    sku = scrapy.Field()
    image_links = scrapy.Field()
    url = scrapy.Field()
