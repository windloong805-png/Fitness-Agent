"""
Fitness-Agent 数据库连接配置。

模块说明：
提供 SQLAlchemy Engine、SessionLocal 和 Base，供后端各业务模块定义 ORM 模型与获取数据库会话。
当前项目要求连接本地 MySQL 数据库 fitness_agent，不再默认回退到 SQLite。

论文映射说明：
对应模块：M8 数据存储模块
对应论文：第三章 数据库设计；第六章 后端实现
"""

from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured. Copy .env.example to .env and set a MySQL connection string."
    )

if not DATABASE_URL.startswith("mysql"):
    raise RuntimeError("DATABASE_URL must use a MySQL driver, for example mysql+pymysql://user:password@127.0.0.1:3306/fitness_agent")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式模型基类。"""


def verify_database_connection() -> None:
    """
    验证数据库连接。

    函数说明：
    在 FastAPI 启动阶段执行 `SELECT 1`，确保后端能够连接到本地 MySQL 数据库 fitness_agent。
    """

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def get_db():
    """
    获取数据库会话。

    函数说明：
    FastAPI 依赖函数。每次请求创建一个数据库会话，请求结束后自动关闭。
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
