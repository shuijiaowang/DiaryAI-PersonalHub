# dao.py
from sqlalchemy.orm import Session
from datetime import date  # 用于日期类型适配

from model.models import User  # 导入User模型（替换原WebsiteFile）


class UserDAO:
    """用户DAO层，封装用户表所有数据库操作"""

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        age: int,
        birthday: str | date,  # 支持字符串（如"1999-05-15"）或date对象
        settings: dict | str = None  # 支持字典或JSON字符串
    ):
        """新增用户记录
        :param db: 数据库会话
        :param username: 用户名
        :param age: 年龄
        :param birthday: 出生日期（格式：YYYY-MM-DD）
        :param settings: 用户设置（JSON字典/字符串，可选）
        :return: 创建后的User对象
        """
        try:
            # 处理settings类型：如果是字典则自动转JSON，字符串直接使用
            if isinstance(settings, dict):
                import json
                settings = json.dumps(settings)

            user = User(
                username=username,
                age=age,
                birthday=birthday,  # SQLAlchemy自动将字符串转为date类型
                settings=settings
            )
            db.add(user)
            db.commit()  # 提交事务
            db.refresh(user)  # 刷新获取自增ID
            return user
        except Exception as e:
            db.rollback()  # 异常回滚
            raise e

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """根据ID查询用户
        :param db: 数据库会话
        :param user_id: 用户ID
        :return: User对象 | None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_users_by_username(db: Session, username: str):
        """根据用户名模糊查询用户
        :param db: 数据库会话
        :param username: 用户名关键词
        :return: User对象列表
        """
        return db.query(User).filter(User.username.like(f"%{username}%")).all()

    @staticmethod
    def update_user_info(
        db: Session,
        user_id: int,
        age: int = None,
        settings: dict | str = None
    ):
        """更新用户信息（支持年龄/设置的部分更新）
        :param db: 数据库会话
        :param user_id: 用户ID
        :param age: 新年龄（可选）
        :param settings: 新设置（JSON字典/字符串，可选）
        :return: 是否更新成功（bool）
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False

            # 只更新传入的字段（部分更新）
            if age is not None:
                user.age = age
            if settings is not None:
                # 统一转为JSON字符串（如果是字典）
                if isinstance(settings, dict):
                    import json
                    settings = json.dumps(settings)
                user.settings = settings

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_user(db: Session, user_id: int):
        """删除用户记录
        :param db: 数据库会话
        :param user_id: 用户ID
        :return: 是否删除成功（bool）
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e


"""
from dao.dao import UserDAO

# 1. 创建用户
user = UserDAO.create_user(
    db=db,
    username="zhangsan",
    age=25,
    birthday="1999-05-15",
    settings={"theme": "dark", "notifications": True}
)

# 2. 查询用户
user = UserDAO.get_user_by_id(db, user_id=1)
users = UserDAO.get_users_by_username(db, username="zhang")

# 3. 更新用户
UserDAO.update_user_info(db, user_id=1, age=26, settings={"theme": "light"})

# 4. 删除用户
UserDAO.delete_user(db, user_id=1)
"""