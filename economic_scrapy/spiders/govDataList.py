# -*- coding: utf-8 -*-
import scrapy
# from scrapy.pipelines import MySQLPipeline

class GovdatalistSpider(scrapy.Spider):
    name = 'govDataList'
    # allowed_domains = ['data.stats.gov.cn']
    basic_url = 'https://data.stats.gov.cn/easyquery.htm'
    start_urls = ['https://blog.scrapinghub.com']

    def parse(self, response):
        yield {
            "id": "A01111",
            "pid": "",
            "wdcode": "zb",
            "dbcode": "decode",
            "isParent": True,
            "name": "价格指数"
        }

        # for next_page in response.css('a.next-posts-link'):
        #     yield response.follow(next_page, self.parse)
