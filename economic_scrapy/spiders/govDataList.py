# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlencode

from economic_scrapy.db.category_db import CategoryBo, CategoryDao

# logger = Logs.get_log(__name__)


class GovdatalistSpider(scrapy.Spider):
    name = 'govDataList'
    # allowed_domains = ['data.stats.gov.cn']
    basic_url = 'https://data.stats.gov.cn/easyquery.htm'
    start_urls = ['https://data.stats.gov.cn/easyquery.htm']

    def parse(self, response):
        category_list = CategoryDao.get_child_list()
        for category in category_list[:1]:

            params = {"wdcode": "sj", "valuecode": "1949-"}
            print(urlencode(params, True))

            query = {
                "m": "QueryData",
                "dbcode": category.dbcode,
                "rowcode": "zb",
                "colcode": "sj",
                "wds": [],
                # "dfwds[]": '[{"wdcode": "sj", "valuecode": "1949-"}]'
            }

            yield scrapy.Request(
                url=self.basic_url + "?" + urlencode(query) + "&dfwds=[{%22wdcode%22:%22sj%22,%22valuecode%22:%221949-%22}]",
                callback=self.parse_data
            )

    def parse_data(self, response):
        if response is None:
            return

        body = json.loads(response.body)

        if body["returncode"] == 200:
            print(body["returndata"]["datanodes"])
        else:
            print('scrapy error')
