# -*- coding: utf-8 -*-
import scrapy
from economic_scrapy.db.category_db import CategoryBo, CategoryDao

# logger = Logs.get_log(__name__)


class GovdatalistSpider(scrapy.Spider):
    name = 'govDataList'
    # allowed_domains = ['data.stats.gov.cn']
    basic_url = 'https://data.stats.gov.cn/easyquery.htm'
    start_urls = ['https://blog.scrapinghub.com']

    def parse(self, response):
        category_list = CategoryDao.get_child_list()
        print(category_list)
        # for category in category_list:
        #     print(category.name)

        # print('parse')
        # yield scrapy.Request(
        #     url=self.basic_url,
        #     formdata={
        #         "id": "zb",
        #         "dbcode": "hgyd",
        #         "wdcode": "zb",
        #         "m": "getTree"
        #     },
        #     callback=self.parse_column
        # )
