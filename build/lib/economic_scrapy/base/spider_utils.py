from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from economic_scrapy.base.common import CommonParam


class DBUtil:
    bp_pool = None
    param = CommonParam

    @classmethod
    def get_session(cls):
        # 初始化数据库连接:
        cls.bp_pool = create_engine(
            cls.param.database_url,
            pool_size=cls.param.database_pool_size,
            max_overflow=cls.param.database_max_overflow,
            pool_recycle=3600 * 6
        ) if cls.bp_pool is None else cls.bp_pool

        # 创建DBSession类型
        db_session = sessionmaker(bind=cls.bp_pool)
        session = db_session()
        return session


class BeanUtil:
    @staticmethod
    def copy_obj_properties(_from=None, to=None):
        fields = dir(_from)
        for field in fields:
            if not (field.startswith("__") or field.startswith("_")):
                if getattr(_from, field) is not None:
                    if hasattr(to, field):
                        # print(field)
                        setattr(to, field, getattr(_from, field))
                        # print(getattr(to, field))
        return to

    @staticmethod
    def copy_dict_properties(_from=None, to=None):
        for key in _from:
            if _from[key] is not None:
                to[key] = _from[key]
        return to


def main():
    print('main')


if __name__ == "__main__":
    main()
