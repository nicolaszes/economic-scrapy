# -*- coding: utf-8 -*-
import scrapy
import json

class GovdataSpider(scrapy.Spider):
    name = 'govDataCategory'
    # allowed_domains = ['data.stats.gov.cn']
    basic_url = 'https://data.stats.gov.cn/easyquery.htm'
    start_urls = ['https://data.stats.gov.cn/easyquery.htm']

    def parse(self, response):
        yield scrapy.FormRequest(
            url=self.basic_url,
            formdata={
                "id": "zb",
                "dbcode": "hgyd",
                "wdcode": "zb",
                "m": "getTree"
            },
            callback=self.parse_column
        )

    def parse_column(self, response):
        column_str = response.css('body p').get().replace(
            '<p>', '').replace('</p>', '')
        for column in json.loads(column_str):
            column["decode"] = column["name"].encode().decode()
            print(column)
            
            yield scrapy.FormRequest(
                url=self.basic_url,
                formdata={
                    "id": column["id"],
                    "dbcode": column["dbcode"],
                    "wdcode": column["wdcode"],
                    "m": "getTree"
                },
                callback=self.parse_column
            )

            yield column
    
