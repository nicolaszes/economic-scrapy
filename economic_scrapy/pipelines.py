# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class MySQLPipeline(object):
    # 打开数据库
    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME')
        host = spider.settings.get('MYSQL_HOST')
        port = spider.settings.get('MYSQL_PORT')
        user = spider.settings.get('MYSQL_USER')
        passwd = spider.settings.get('MYSQL_PASSWORD')

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
        if self.search_db(item) is None:
            self.insert_db(item)
        else:
            self.update_db(item)
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

        sql = 'INSERT INTO t_month_category VALUES(%s,%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)

    def update_db(self, item):
        self.db_cur.execute(
            """update t_month_category set pid=%s, wdcode=%s, dbcode=%s, isParent=%s, name=%s where id=%s""",
            (item['pid'], item['wdcode'], item['dbcode'], item['isParent'], item['name'], item['id'])
        )
        self.db_conn.commit()

    # 查询数据
    def search_db(self, item):
        self.db_cur.execute("""SELECT * from t_month_category where id = %s""", (item["id"]))
        result = self.db_cur.fetchone()

        return result

    def delete_db(self, item):
        self.db_cur.execute("""delete from t_month_category where id<=%s""", (item["id"]))
        self.db_conn.commit()

class EconomicScrapyPipeline(object):
    def process_item(self, item, spider):
        return item
