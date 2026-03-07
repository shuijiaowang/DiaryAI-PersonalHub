import psycopg2
from psycopg2 import OperationalError


def connect_postgresql():
    """
    初始化连接PostgreSQL数据库
    返回：连接对象（conn）/游标对象（cur），连接失败返回None
    """
    # 数据库配置（根据你的实际情况修改）
    db_config = {
        "host": "localhost",  # 数据库地址，本地用localhost
        "database": "pg_test",  # 你创建的数据库名
        "user": "postgres",  # 默认超级用户
        "password": "123456",  # 安装PostgreSQL时设置的密码
        "port": 5432  # 默认端口，无需修改
    }

    conn = None
    cur = None
    try:
        # 1. 建立数据库连接
        conn = psycopg2.connect(**db_config)
        # 2. 创建游标（用于执行SQL语句）
        cur = conn.cursor()
        print("✅ 数据库连接成功！")

        # 测试：执行简单SQL（可选）
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"📌 PostgreSQL版本：{db_version[0]}")

        return conn, cur

    except OperationalError as e:
        # 捕获连接异常（如密码错误、数据库不存在等）
        print(f"❌ 数据库连接失败：{e}")
        return None, None


if __name__ == "__main__":
    # 初始化连接
    conn, cur = connect_postgresql()

    # 后续操作（如执行SQL）示例
    if conn and cur:
        try:
            # 2. 插入两条数据（修复核心：使用executemany）
            insert_sql = """
                         INSERT INTO "user" (id, username, age, birthday, config)
                         VALUES (%s, %s, %s, %s, %s);                    
                         """
            # 数据列表：每个元组对应一条数据
            data_list = [
                (1, "zhangsan", 25, "1999-05-15", '{"theme": "dark", "notifications": true}'),
                (2, "lisi", 30, "1994-11-20", '{"theme": "light", "notifications": false}')
            ]
            # 批量执行插入（executemany适配多条数据）
            cur.executemany(insert_sql, data_list)
            print(f"✅ 成功插入 {cur.rowcount} 条数据")

            # 提交事务
            conn.commit()

            # 插入后查询验证
            cur.execute("SELECT * FROM user;")
            result = cur.fetchall()
            print("📋 插入后查询结果：")
            for row in result:
                print(row)

        except Exception as e:
            # 出错时回滚
            conn.rollback()
            print(f"❌ SQL执行失败：{e}")

        finally:
            # 关闭游标和连接
            if cur:
                cur.close()
            if conn:
                conn.close()
                print("🔌 数据库连接已关闭")