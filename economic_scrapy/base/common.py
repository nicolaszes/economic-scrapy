# -*- coding: utf-8 -*-
import configparser
import os


class CommonParam:
    base_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(base_dir, "common.ini")  # 配置文件名称
    config = configparser.ConfigParser()
    config.read(config_file_path, encoding="utf-8-sig")

    # 数据库链接
    # database_url = config["database"]["url"]
    # database_pool_size = int(config["database"]["pool_size"])
    # database_max_overflow = int(config["database"]["max_overflow"])

    database_url = "mysql+pymysql://root:Nicolas199@localhost:3306/category_db"
    database_pool_size = 50
    database_max_overflow = 300