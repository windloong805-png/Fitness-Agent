"""
M3 训练收益评估模块计算器。

模块说明：
本文件负责把公式层、Schema 层和 M1 用户画像模块连接起来。
它不定义数据库模型，而是读取 M1 输出的 AgentContext，再计算 M3 的训练收益评价结果。

数据流说明：
1. 直接计算：RewardInput -> formulas -> RewardOutput。
2. Agent 集成：user_id -> M1 get_profile -> M1 AgentContext -> M3 RewardOutput -> M3 AgentContextSchema。

论文映射说明：
对应模块：M3 训练收益评估模块
对应论文：第四章 4.2 训练收益评估模型设计
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.profile.service import get_profile
from backend.reward.formulas import (
    calculate_fatigue,
    calculate_recovery,
    calculate_total_reward,
    calculate_training_benefit,
)
from backend.reward.schemas import AgentContextSchema, RewardComputedState, RewardInput, RewardOutput, RewardWeights


def calculate_reward(reward_input: RewardInput) -> RewardOutput:
    """
    计算完整训练收益结果。

    函数说明：
    该函数把 Recovery、Fatigue、TrainingBenefit、TotalReward 串联起来，
    是 M3 对外提供给 M4 动态规划模块的评价函数入口。

    输入参数：
    reward_input：包含睡眠、疲劳、训练负荷、训练动作和权重的 RewardInput。

    返回参数：
    RewardOutput：包含 recovery、fatigue、training_benefit、total_reward 和解释信息。
    """

    recovery = calculate_recovery(
        sleep_hours=reward_input.sleep_hours,
        sleep_quality_score=reward_input.sleep_quality_score,
        fatigue_score=reward_input.current_fatigue_score,
        stress_score=reward_input.stress_score,
    )
    fatigue = calculate_fatigue(
        training_load=reward_input.training_load,
        soreness_count=reward_input.soreness_count,
        stress_score=reward_input.stress_score,
    )
    training_benefit = calculate_training_benefit(
        training_type=reward_input.training_type,
        intensity=reward_input.intensity,
        duration=reward_input.duration,
        goal_match_score=reward_input.goal_match_score,
    )
    total_reward = calculate_total_reward(
        recovery=recovery,
        fatigue=fatigue,
        training_benefit=training_benefit,
        w1=reward_input.weights.w1,
        w2=reward_input.weights.w2,
        w3=reward_input.weights.w3,
    )

    return RewardOutput(
        recovery=recovery,
        fatigue=fatigue,
        training_benefit=training_benefit,
        total_reward=total_reward,
        explanation={
            "recovery": "恢复指数综合睡眠时长、睡眠质量、已有疲劳和压力，值越高越适合训练。",
            "fatigue": "疲劳指数综合近期训练负荷、酸痛部位数量和压力，值越高越需要恢复。",
            "training_benefit": "训练收益综合训练类型、强度、时长和目标匹配度，用于衡量本次训练价值。",
            "total_reward": "综合收益采用 w1*训练收益 + w2*恢复 - w3*疲劳，为动态规划提供可解释评价函数。",
        },
    )


def build_reward_context(
    user_id: int,
    db: Session | None = None,
    training_type: str | None = None,
    intensity: str | float | int | None = None,
    duration: float | None = None,
    goal_match_score: float | None = None,
    training_load: float | None = None,
    soreness_count: float | None = None,
    stress_score: float | None = None,
    sleep_quality_score: float | None = None,
    weights: RewardWeights | None = None,
) -> AgentContextSchema:
    """
    构建包含 M3 训练收益评估结果的 AgentContext。

    函数说明：
    该函数从 M1 用户画像模块读取 profile、goal、daily_status、constraints、preferences，
    然后计算 bmi、recovery、fatigue、training_benefit、total_reward。
    这样设计是为了遵守 Agent 开发规范：后续 M4 和 M5 使用 AgentContext，而不是跨模块直接读数据库。

    输入参数：
    user_id：用户 ID。
    db：可选数据库会话。接口层或调度层已有会话时应传入，避免重复创建连接。
    training_type/intensity/duration/goal_match_score：候选训练动作特征，供 M4 评价不同动作。
    weights：综合收益权重，后续可由实验配置或系统设置传入。

    返回参数：
    AgentContextSchema：包含 M1 原始上下文和 M3 computed_state 的扩展 AgentContext。
    """

    if db is None:
        with SessionLocal() as local_db:
            return _build_reward_context_with_db(
                user_id=user_id,
                db=local_db,
                training_type=training_type,
                intensity=intensity,
                duration=duration,
                goal_match_score=goal_match_score,
                training_load=training_load,
                soreness_count=soreness_count,
                stress_score=stress_score,
                sleep_quality_score=sleep_quality_score,
                weights=weights,
            )

    return _build_reward_context_with_db(
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
        weights=weights,
    )


def _build_reward_context_with_db(
    user_id: int,
    db: Session,
    training_type: str | None,
    intensity: str | float | int | None,
    duration: float | None,
    goal_match_score: float | None,
    training_load: float | None,
    soreness_count: float | None,
    stress_score: float | None,
    sleep_quality_score: float | None,
    weights: RewardWeights | None,
) -> AgentContextSchema:
    """
    使用指定数据库会话构建 M3 AgentContext。

    函数说明：
    内部函数用于避免 build_reward_context 中重复代码。它保持数据流清晰：
    M1 ProfileRead -> RewardInput -> RewardOutput -> AgentContextSchema。
    """

    profile_read = get_profile(db, user_id)
    m1_context = profile_read.agent_context
    daily_status = m1_context.daily_status

    inferred_training_type = training_type or _infer_training_type(m1_context.goal, m1_context.preferences)
    inferred_intensity = intensity or _infer_intensity(m1_context.constraints)
    inferred_duration = duration if duration is not None else 45.0
    inferred_goal_match = goal_match_score if goal_match_score is not None else _infer_goal_match(m1_context.goal)
    inferred_training_load = training_load if training_load is not None else daily_status.get("rpe")
    inferred_soreness_count = soreness_count if soreness_count is not None else _infer_soreness_count(daily_status)
    inferred_stress = stress_score if stress_score is not None else 3.0

    reward_input = RewardInput(
        sleep_hours=daily_status.get("sleep_hours"),
        sleep_quality_score=sleep_quality_score,
        current_fatigue_score=daily_status.get("fatigue_score"),
        stress_score=inferred_stress,
        training_load=inferred_training_load,
        soreness_count=inferred_soreness_count,
        training_type=inferred_training_type,
        intensity=inferred_intensity,
        duration=inferred_duration,
        goal_match_score=inferred_goal_match,
        weights=weights or RewardWeights(),
    )
    reward_output = calculate_reward(reward_input)

    return AgentContextSchema(
        profile=m1_context.profile,
        goal=m1_context.goal,
        daily_status=m1_context.daily_status,
        constraints=m1_context.constraints,
        preferences=m1_context.preferences,
        computed_state=RewardComputedState(
            bmi=m1_context.computed_state.bmi,
            recovery=reward_output.recovery,
            fatigue=reward_output.fatigue,
            training_benefit=reward_output.training_benefit,
            total_reward=reward_output.total_reward,
        ),
    )


def _infer_training_type(goal: dict, preferences: list[dict]) -> str:
    """从目标和偏好中推断训练类型，缺失时返回 strength 作为默认候选动作。"""

    for preference in preferences:
        if preference.get("preference_type") in {"training_type", "preferred_training_type"}:
            return str(preference.get("value") or "strength")

    primary_goal = str(goal.get("primary_goal") or "").lower()
    if "减脂" in primary_goal or "fat" in primary_goal:
        return "cardio"
    if "心肺" in primary_goal or "cardio" in primary_goal:
        return "cardio"
    return "strength"


def _infer_intensity(constraints: list[dict]) -> str:
    """根据健康限制粗略推断默认强度，有高风险限制时降低为 low。"""

    for constraint in constraints:
        if str(constraint.get("severity") or "").lower() == "high":
            return "low"
    return "medium"


def _infer_goal_match(goal: dict) -> float:
    """根据目标存在性给出默认目标匹配分。目标越明确，默认匹配分越高。"""

    if goal.get("primary_goal"):
        return 8.0
    return 6.0


def _infer_soreness_count(daily_status: dict) -> float:
    """从 M1 的 soreness_level 粗略估算酸痛部位数量。"""

    soreness_level = daily_status.get("soreness_level")
    if soreness_level is None:
        return 0.0
    return min(float(soreness_level), 5.0)
