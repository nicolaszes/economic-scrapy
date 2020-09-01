# -*- coding: utf-8 -*-
import scrapy
import json
import re

from urllib.parse import urlencode

from economic_scrapy.db.category_db import MonthCategoryDao
from economic_scrapy.db.monthly_db import MonthlyBo, MonthlyDao

from economic_scrapy.base.exception_decor import exception
from economic_scrapy.logging.logging_utils import Logs

Logs.init_log_config("govDataList")
logger = Logs.get_log(__name__)


class GovdatalistSpider(scrapy.Spider):
    name = 'govDataList'
    # allowed_domains = ['data.stats.gov.cn']
    basic_url = 'https://data.stats.gov.cn/easyquery.htm'
    start_urls = ['https://data.stats.gov.cn/easyquery.htm']

    @exception
    def parse(self, response):
        category_list = MonthCategoryDao.get_child_list()
        for category in category_list[20:30]:
            query = {
                "m": "QueryData",
                "dbcode": category.dbcode,
                "rowcode": "zb",
                "colcode": "sj",
                "wds": [],
                # "dfwds[]": '[{"wdcode": "sj", "valuecode": "1949-"}]'
            }

            print(category.name)
            # https://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgyd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{%22wdcode%22:%22sj%22,%22valuecode%22:%221949-%22},%20{%22wdcode%22:%22zb%22,%22valuecode%22:%22A010102%22}]
            url = self.basic_url + "?" + urlencode(query) + "&dfwds=[{%22wdcode%22:%22zb%22,%22valuecode%22:%22" + category.id + "%22},{%22wdcode%22:%22sj%22,%22valuecode%22:%221949-%22}]"
            yield scrapy.Request(
                url=url,
                callback=self.parse_data
            )

    @exception
    def parse_data(self, response):
        if response is None:
            return

        body = json.loads(response.body)

        if body["returncode"] != 200:
            return

        index_wdnodes = body["returndata"]["wdnodes"][0]["nodes"]

        for node in body["returndata"]["datanodes"]:
            if node["data"]["hasdata"] is False:
                continue

            monthly_bo = MonthlyBo()
            match_obj = re.match(r'zb.(.*)_sj.(.*)', node["code"], re.M | re.I)

            monthly_bo.metrics = match_obj.group(1)
            monthly_bo.month = match_obj.group(2)
            monthly_bo.value = node["data"]["data"]

            for item in list(filter(lambda x: x["code"] == monthly_bo.metrics, index_wdnodes)):
                monthly_bo.name = item["name"]

            if MonthlyDao.get_pid(monthly_bo):
                MonthlyDao.update_detail(monthly_bo)
            else:
                MonthlyDao.insert(monthly_bo)

