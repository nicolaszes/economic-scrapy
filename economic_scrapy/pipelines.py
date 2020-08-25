# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class MySQLPipeline(object):
    # 打开数据库
    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME', 'category_db')
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', 'Nicolas199')

        self.db_conn = pymysql.connect(
            host=host,
            port=port,
            db=db,
            user=user,
            passwd=passwd,
            charset='utf8'
        )

        self.db_cur = self.db_conn.cursor()

    # 关闭数据库
    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    # 对数据进行处理
    def process_item(self, item, spider):
        print(item)
        self.insert_db(item)
        return item

    # 插入数据
    def insert_db(self, item):
        values = (
            item['id'],
            item['pid'],
            item['wdcode'],
            item['dbcode'],
            item['isParent'],
            item['name'],
        )

        sql = 'INSERT INTO category VALUES(%s,%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)


class EconomicScrapyPipeline(object):
    def process_item(self, item, spider):
        return item
