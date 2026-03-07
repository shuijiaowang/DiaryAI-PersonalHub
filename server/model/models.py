# models.py
from sqlalchemy import Column, Integer, String, Date, JSON,DateTime,func

from db.config import Base


class User(Base):
    __tablename__ = "users"  # 数据库表名，与数据场景匹配

    # 字段定义（严格对应 data_list 中的数据项）
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), nullable=False, comment="用户名")  # 对应 "zhangsan"/"lisi"
    age = Column(Integer, nullable=False, comment="年龄")  # 对应 25/30
    birthday = Column(Date, nullable=False, comment="出生日期")  # 对应 "1999-05-15" 这类日期
    settings = Column(JSON, comment="用户个性化设置（JSON格式）")  # 对应 JSON 字符串

    # 可选：如果需要记录创建时间，可保留此字段（data_list 无，按需添加）
    create_time = Column(DateTime, default=func.now(), comment="记录创建时间")

    # 自定义打印格式，方便调试
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, age={self.age})>"