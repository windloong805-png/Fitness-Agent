"""
M1 用户画像模块数据库结构重建脚本。

模块说明：
删除 MySQL 中已有的 M1 用户画像相关旧表，并按照 backend/profile/models.py 中的 ORM 模型重新创建表结构。
本脚本以项目代码字段为唯一标准，用于纠正手工建表或历史临时表结构与代码模型不一致的问题。

论文映射说明：
对应模块：M1 用户画像模块；M8 数据存储模块
对应论文：第三章 数据库设计；第四章 用户画像模型设计；第六章 系统实现
"""

from sqlalchemy import text

from backend.database import Base, engine, verify_database_connection
import backend.profile.models


OLD_AND_CURRENT_TABLES = [
    "daily_statuses",
    "daily_status",
    "user_preferences",
    "user_constraints",
    "user_goals",
    "user_profiles",
    "users",
]


def reset_profile_schema() -> None:
    """
    重建 M1 用户画像模块数据表。

    函数说明：
    先关闭外键检查，删除旧表，再开启外键检查并执行 SQLAlchemy create_all。
    注意：该操作会清空上述表中的已有数据。
    """

    verify_database_connection()
    with engine.begin() as connection:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table_name in OLD_AND_CURRENT_TABLES:
            connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_profile_schema()
    print("M1 profile schema reset completed.")
