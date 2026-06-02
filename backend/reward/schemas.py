"""
M3 训练收益评估模块 Pydantic Schema。

模块说明：
定义训练收益评估的输入、输出和 AgentContext 扩展结构。
Schema 是 M3 与 M4 动态规划模块、M5 Qwen 交互模块之间的数据契约。

数据流说明：
RewardInput -> calculator.calculate_reward -> RewardOutput；
M1 AgentContext -> calculator.build_reward_context -> AgentContextSchema。

论文映射说明：
对应模块：M3 训练收益评估模块
对应论文：第四章 4.2 训练收益评估模型设计
"""

from typing import Any

from pydantic import BaseModel, Field


class RewardWeights(BaseModel):
    """
    综合收益权重 Schema。

    类说明：
    权重独立成结构，是为了后续论文实验可以比较不同权重组合对训练计划生成的影响。
    """

    w1: float = Field(default=0.5, ge=0.0, description="训练收益权重")
    w2: float = Field(default=0.3, ge=0.0, description="恢复指数权重")
    w3: float = Field(default=0.2, ge=0.0, description="疲劳惩罚权重")


class RewardInput(BaseModel):
    """
    训练收益评估输入 Schema。

    类说明：
    该结构把恢复、疲劳和训练价值所需的变量集中在一起，
    便于 M4 动态规划模块对不同候选训练动作反复调用同一评价函数。
    """

    sleep_hours: float | None = Field(default=None, ge=0.0, le=24.0)
    sleep_quality_score: float | None = Field(default=None, ge=0.0)
    current_fatigue_score: float | None = Field(default=None, ge=0.0)
    stress_score: float | None = Field(default=None, ge=0.0)
    training_load: float | None = Field(default=None, ge=0.0)
    soreness_count: float | None = Field(default=None, ge=0.0)
    training_type: str | None = None
    intensity: str | float | int | None = None
    duration: float | None = Field(default=None, ge=0.0)
    goal_match_score: float | None = Field(default=None, ge=0.0)
    weights: RewardWeights = Field(default_factory=RewardWeights)


class RewardOutput(BaseModel):
    """
    训练收益评估输出 Schema。

    类说明：
    输出结果既服务 M4 动态规划的数值优化，也服务 Qwen2.5 的可解释文本生成。
    """

    recovery: float
    fatigue: float
    training_benefit: float
    total_reward: float
    explanation: dict[str, str] = Field(default_factory=dict)


class RewardComputedState(BaseModel):
    """
    Reward AgentContext 计算状态 Schema。

    类说明：
    在 M1 的 computed_state 基础上加入 M3 的 training_benefit 和 total_reward，
    使后续 Agent 能力不需要跨模块读取数据库。
    """

    bmi: float | None = None
    recovery: float
    fatigue: float
    training_benefit: float
    total_reward: float


class AgentContextSchema(BaseModel):
    """
    M3 扩展 AgentContext Schema。

    类说明：
    该结构保留 M1 的 profile、goal、daily_status、constraints、preferences，
    并在 computed_state 中加入训练收益评估结果。
    """

    profile: dict[str, Any]
    goal: dict[str, Any]
    daily_status: dict[str, Any]
    constraints: list[dict[str, Any]]
    preferences: list[dict[str, Any]]
    computed_state: RewardComputedState
