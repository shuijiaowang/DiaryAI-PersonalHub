# config.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 统一配置
DB_CONFIG = {
    "host": "localhost",
    "database": "pg_test",
    "user": "postgres",
    "password": "123456",
    "port": 5432,
    "echo_sql": True
}

# 创建引擎
DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DATABASE_URL, echo=DB_CONFIG["echo_sql"])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 初始化表
def init_db():
    from model.models import User  # 根据你的实际目录结构调整导入路径
    Base.metadata.create_all(bind=engine)