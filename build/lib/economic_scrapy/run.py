# -*- coding: utf-8 -*-
# @Time     : 2020/08/26 20:48
# @Author   : nicolas zes


from scrapy import cmdline


name = 'govMonthDataList'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())