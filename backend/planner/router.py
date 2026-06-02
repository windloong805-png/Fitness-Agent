"""
M4 动态规划训练决策模块 FastAPI 路由。

模块说明：
提供 7 天训练计划生成接口。接口层只负责接收请求和返回响应，核心动态规划逻辑放在 planner.py。

数据流说明：
POST /api/planner/plan_weekly -> PlannerRequest -> plan_weekly_training() -> WeeklyPlanResponse。

论文映射说明：
对应模块：M4 动态规划训练决策模块
对应论文：第四章 4.3 动态规划训练决策模型设计
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.planner.planner import plan_weekly_training
from backend.planner.schemas import PlannerRequest, WeeklyPlanResponse


router = APIRouter(prefix="/api/planner", tags=["M4 动态规划训练决策模块"])


@router.post("/plan_weekly", response_model=WeeklyPlanResponse)
def plan_weekly(payload: PlannerRequest, db: Annotated[Session, Depends(get_db)]) -> WeeklyPlanResponse:
    """
    生成未来 7 天训练计划接口。

    函数说明：
    接口支持输入 user_id 或直接输入 AgentContext。若输入 user_id，系统读取 M1 用户画像和 M3 RewardContext；
    若输入 AgentContext，则直接进行动态规划搜索。

    输入参数：
    payload.user_id：用户 ID。
    payload.agent_context：可选 M3 AgentContext，用于实验或调试。

    返回参数：
    WeeklyPlanResponse：7 天最优训练计划 JSON。

    对应模块：
    M4 动态规划训练决策模块。

    对应论文：
    第四章 4.3 动态规划训练决策模型设计。
    """

    return plan_weekly_training(user_id=payload.user_id, agent_context=payload.agent_context, db=db)
