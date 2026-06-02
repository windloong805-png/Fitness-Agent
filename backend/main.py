"""
Fitness-Agent FastAPI 应用入口。

模块说明：
创建 FastAPI 应用实例，注册用户画像模块路由，并在开发阶段自动创建数据库表。

论文映射说明：
对应模块：M1 用户画像模块；M8 数据存储模块
对应论文：第四章 用户画像模型设计；第六章 系统实现
"""

from fastapi import FastAPI

from backend.database import Base, engine, verify_database_connection
from backend.planner.router import router as planner_router
from backend.profile.router import router as profile_router
from backend.reward.router import router as reward_router


app = FastAPI(
    title="Fitness-Agent API",
    description="融合知识增强与动态规划的健身智能体后端接口",
    version="0.1.0",
)

app.include_router(profile_router)
app.include_router(reward_router)
app.include_router(planner_router)


@app.on_event("startup")
def create_database_tables():
    """
    初始化数据库表。

    函数说明：
    开发阶段自动创建用户画像相关数据表；后续接入 Alembic 后可替换为迁移流程。
    """

    verify_database_connection()
    Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    """
    服务健康检查。

    函数说明：
    返回后端服务运行状态，便于本地开发和接口连通性验证。
    """

    return {"name": "Fitness-Agent", "status": "running"}
