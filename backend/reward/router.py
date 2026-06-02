"""
M3 训练收益评估模块 FastAPI 路由。

模块说明：
本文件为 M3 提供 HTTP 接口，主要服务前端展示、接口调试、论文答辩演示和后续 M4 动态规划模块联调。
M4 在后端内部正式调用时仍应优先调用 calculator.py 中的 Python 函数，而不是通过 HTTP 调用本服务。

数据流说明：
1. POST /api/reward/calculate:
   前端或调试工具提交 RewardInput -> M3 calculate_reward -> RewardOutput。
2. GET /api/reward/context/{user_id}:
   user_id -> M1 用户画像模块 -> M3 build_reward_context -> AgentContextSchema。

论文映射说明：
对应模块：M3 训练收益评估模块
对应论文：第四章 4.2 训练收益评估模型设计
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.reward.calculator import build_reward_context, calculate_reward
from backend.reward.schemas import AgentContextSchema, RewardInput, RewardOutput


router = APIRouter(prefix="/api/reward", tags=["M3 训练收益评估模块"])


@router.post("/calculate", response_model=RewardOutput)
def calculate_training_reward(payload: RewardInput) -> RewardOutput:
    """
    训练收益直接计算接口。

    函数说明：
    输入一组用户状态与候选训练动作特征，返回 recovery、fatigue、training_benefit 和 total_reward。
    该接口适合用于前端调试、论文演示和 M3 公式验证。

    输入参数：
    payload：RewardInput，包含睡眠、疲劳、训练负荷、训练动作、目标匹配分和权重。

    返回参数：
    RewardOutput，包含四类收益评估指标和可解释说明。

    对应模块：
    M3 训练收益评估模块。

    对应论文：
    第四章 4.2 训练收益评估模型设计。
    """

    return calculate_reward(payload)


@router.get("/context/{user_id}", response_model=AgentContextSchema)
def get_reward_context(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    training_type: Annotated[str | None, Query(description="候选训练类型，如 strength/cardio/hiit")] = None,
    intensity: Annotated[str | None, Query(description="候选训练强度，如 low/medium/high")] = None,
    duration: Annotated[float | None, Query(ge=0, description="候选训练时长，单位分钟")] = None,
    goal_match_score: Annotated[float | None, Query(ge=0, description="目标匹配分，支持 0~10 或 0~100")] = None,
    training_load: Annotated[float | None, Query(ge=0, description="近期训练负荷，支持 0~10 或 0~100")] = None,
    soreness_count: Annotated[float | None, Query(ge=0, description="酸痛部位数量")] = None,
    stress_score: Annotated[float | None, Query(ge=0, description="压力评分，支持 0~10 或 0~100")] = None,
    sleep_quality_score: Annotated[float | None, Query(ge=0, description="睡眠质量评分，支持 0~10 或 0~100")] = None,
) -> AgentContextSchema:
    """
    构建 M3 扩展 AgentContext 接口。

    函数说明：
    根据 user_id 读取 M1 用户画像模块的标准 AgentContext，并计算 M3 训练收益评估结果。
    该接口适合前端数据页、计划页和论文演示展示“用户状态 -> 奖励函数”的完整链路。

    输入参数：
    user_id：用户 ID。
    query 参数：可选训练动作特征和评分参数，用于模拟不同候选训练方案。

    返回参数：
    AgentContextSchema，包含 profile、goal、daily_status、constraints、preferences 和扩展 computed_state。

    对应模块：
    M3 训练收益评估模块，依赖 M1 用户画像模块。

    对应论文：
    第四章 4.2 训练收益评估模型设计。
    """

    return build_reward_context(
        user_id=user_id,
        db=db,
        training_type=training_type,
        intensity=intensity,
        duration=duration,
        goal_match_score=goal_match_score,
        training_load=training_load,
        soreness_count=soreness_count,
        stress_score=stress_score,
        sleep_quality_score=sleep_quality_score,
    )
