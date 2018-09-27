"""Drjays scrapper."""
import scrapy
from drjays_code.items import DrjaysCodeItem


class DrjaysSpider(scrapy.Spider):
    """Drjays Spider."""
    name = 'drjays'
    start_urls = ['https://www.drjays.com/']

    def parse(self, response):
        """Parses links from homepage."""
        if response.status != 200:
            return
        categories = set(response.xpath('//ul[@class="nav navbar-nav"]/li//a/@href').extract())
        sections = set(response.xpath('//a[@data-toggle="dropdown"]/@href').extract())
        sections.remove('#')
        categories = categories - sections
        yield response.follow(sections.pop(), callback=self.parse_section,
                              meta={"categories": categories, "sections": sections})

    def parse_section(self, response):
        """Parsing links from each section page."""
        if response.status != 200:
            return
        categories = []
        if response.meta["sections"]:
            categories += response.xpath('//div[contains(@class,"section")]/ul/li/a/@href')\
                .extract()
            categories += response.xpath('//div[@class="nav-box"]/div/a/@href').extract()
            categories += response.xpath('//div[contains(@class ,"gutter-20")]/div/div/a/@href')\
                .extract()
            categories += response.meta["categories"]
            categories = set(categories)
            yield response.follow(response.meta["sections"].pop(), callback=self.parse_section,
                                  meta={"categories": categories,
                                        "sections": response.meta["sections"]})
        else:
            categories += response.xpath('//div[contains(@class,"section")]/ul/li/a/@href')\
                .extract()
            categories += response.xpath('//div[@class="nav-box"]/div/a/@href').extract()
            categories += response.xpath('//div[contains(@class ,"gutter-20")]/div/div/a/@href')\
                .extract()
            categories += response.meta["categories"]
            categories = set(categories)
            for category in categories:
                yield response.follow(category, callback=self.parse_brand)

    def parse_brand(self, response):
        """Pasrses links of brands."""
        if response.status != 200:
            return
        brands = response.xpath('//div[@id="brand-names"]/a/@href').extract()
        for brand in brands:
            yield response.follow(brand, callback=self.parse_category)
        if not brands:
            response.follow(response.url, callback=self.parse_category)

    def parse_category(self, response):
        """Parses links of individual products and yields them."""
        if response.status != 200:
            return
        products = response.xpath('//div[@id="products"]/div/a/@href').extract()
        for product in products:
            yield response.follow(product, callback=self.parse_product)
        next_page = response.xpath('//a[@class="pagination_top pagination_next"]/@href')\
            .extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_category)

    def parse_product(self, response):
        """Parses details of products"""
        if response.status != 200:
            return
        product = DrjaysCodeItem()

        product['name'] = response.xpath('//div[@id="column2-pdp"]/h1/text()').extract_first()
        product['maker'] = response.xpath('//div[@id="column2-pdp"]/h2/text()').extract_first()

        sale_price = response.xpath('//span[@class="price"]/text()').extract_first()
        off_price = response.xpath('//span[@class="offprice"]/text()').extract_first()
        product['pricing'] = {"Current Sale Price": sale_price, "Old Price": off_price}

        available_sizes = response.xpath('//div[@data-type="size"]/a/span/text()').extract()
        if not available_sizes:
            available_sizes = response.xpath('//div[@class="product_dropdown"]/a/text()')\
                .extract_first()
        product['available_sizes'] = available_sizes
        product['description'] = response.xpath('//div[@id="product-description"]/ul/li/text()')\
            .extract()
        product['product_id'] = response.xpath('//span[@id="prod-id"]/text()').extract_first()

        about_product = response.xpath('//div[@id="tabs-1"]/text()').extract()
        about_product = [about for about in about_product if len(about) > 4]
        product['fabric'] = about_product[-3]
        product['color'] = about_product[-2]
        product['sku'] = about_product[-1]

        hierarchy = response.xpath('//div[@id="breadcrumb"]/div/a/text()').extract()
        product['collection'] = hierarchy[-1]
        product['category'] = hierarchy[-2]

        product['image_links'] = response.xpath('//div[@id="product-alt-imgs"]/span/img/@src')\
            .extract()
        product['url'] = response.url
        yield product
