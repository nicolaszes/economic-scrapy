from sqlalchemy import Column, String
from sqlalchemy.types import INTEGER, FLOAT

from economic_scrapy.base.db_base import Base
from economic_scrapy.base.spider_utils import DBUtil, BeanUtil


class MonthlyBo(Base):
    # 表的名字:
    __tablename__ = 't_monthly'

    # 表的结构:
    pid = Column(INTEGER, primary_key=True, autoincrement=True)
    metrics = Column(String(255))
    month = Column(String(255))
    value = Column(FLOAT)

    def __init__(
        self,
        pid=None,
        metrics=None,
        month=None,
        value=None
    ):
        self.pid = pid
        self.metrics = metrics
        self.month = month
        self.value = value


class MonthlyDao:
    BO = MonthlyBo

    @classmethod
    def insert(cls, item):
        session = DBUtil.get_session()
        # 插入
        session.add(item)
        session.commit()
        pid = item.pid
        session.close()
        return pid

    @classmethod
    def update_detail(cls, monthly_data: MonthlyBo):
        session = DBUtil.get_session()
        item = session \
            .query(MonthlyBo) \
            .filter(MonthlyBo.metrics == monthly_data.metrics) \
            .filter(MonthlyBo.month == monthly_data.month) \
            .first()
        BeanUtil.copy_obj_properties(monthly_data, item)
        session.commit()
        session.close()

    @classmethod
    def get_pid(cls, monthly_data: MonthlyBo):
        session = DBUtil.get_session()
        item = session \
            .query(MonthlyBo) \
            .filter(MonthlyBo.metrics == monthly_data.metrics) \
            .filter(MonthlyBo.month == monthly_data.month) \
            .first()
        session.commit()
        pid = item.pid if item else item
        session.close()
        return pid

    @classmethod
    def select_all(cls):
        session = DBUtil.get_session()
        res = session.query(cls.BO)
        session.close()
        return res

    # @classmethod
    # def get_child_list(cls):
    #     session = DBUtil.get_session()
    #     res = session \
    #         .query(cls.BO) \
    #         .filter(cls.BO.isParent) \
    #         .all()
    #     session.close()
    #     return res


def main():
    # ScriptInit.env_init()
    param = dict
    param['begin_limit'] = 0
    param['data_size'] = 1000
    print(param)

if __name__ == "__main__":
    main()
