from sqlalchemy import Column, String
from economic_scrapy.base.db_base import Base
from economic_scrapy.base.spider_utils import DBUtil, BeanUtil


class CategoryBo(Base):
    # 表的名字:
    __tablename__ = 'category'

    # 表的结构:
    id = Column(String(255), primary_key=True, autoincrement=False)
    pid = Column(String(255))
    wdcode = Column(String(255))
    dbcode = Column(String(255))
    isParent = Column(String(255))
    name = Column(String(255))

    def __init__(
        self,
        id=None,
        pid=None,
        wdcode=None,
        dbcode=None,
        isParent=None,
        name=None
    ):
        self.id = id
        self.pid = pid
        self.wdcode = wdcode
        self.dbcode = dbcode
        self.isParent = isParent
        self.name = name


class CategoryDao:
    BO = CategoryBo

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
    def update_detail(cls, category: CategoryBo):
        session = DBUtil.get_session()
        item = session \
            .query(CategoryBo) \
            .filter(CategoryBo.id == category.id) \
            .first()
        BeanUtil.copy_obj_properties(category, item)
        session.commit()
        session.close()

    @classmethod
    def select_all(cls):
        session = DBUtil.get_session()
        res = session.query(cls.BO)
        session.close()
        return res

    @classmethod
    def get_child_list(cls):
        session = DBUtil.get_session()
        res = session \
            .query(cls.BO) \
            .filter(cls.BO.isParent is False)
        session.close()
        return res


def main():
    # ScriptInit.env_init()
    param = dict
    param['begin_limit'] = 0
    param['data_size'] = 1000
    print(param)
    # ESRoomModelDao.select_es_room_model_all(param)


if __name__ == "__main__":
    main()
