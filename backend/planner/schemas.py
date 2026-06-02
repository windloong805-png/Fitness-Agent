"""
M4 动态规划训练决策模块 Pydantic Schema。

模块说明：
定义候选训练动作、动作评价结果、每日计划和 7 天计划响应结构。
Schema 是 M4 对 M7 前端展示模块、M5 Qwen 交互模块和后续实验模块的统一数据契约。

数据流说明：
PlannerRequest -> plan_weekly_training() -> WeeklyPlanResponse。

论文映射说明：
对应模块：M4 动态规划训练决策模块
对应论文：第四章 4.3 动态规划训练决策模型设计
"""

from typing import Any

from pydantic import BaseModel, Field, model_validator

from backend.reward.schemas import AgentContextSchema


class TrainingAction(BaseModel):
    """
    候选训练动作 Schema。

    类说明：
    动态规划需要在有限动作集合中搜索最优路径。每个 TrainingAction 表示一天可选的训练方案，
    包含训练类型、强度、时长、目标匹配分和疲劳变化估计。
    """

    action_id: str
    name: str
    training_type: str
    intensity: str
    duration: float = Field(ge=0)
    goal_match_score: float = Field(ge=0)
    fatigue_delta: float = Field(description="执行该动作后预计增加的疲劳桶值")
    recovery_delta: float = Field(default=0.0, description="执行恢复类动作后预计降低的疲劳桶值")
    reason: str


class ActionEvaluation(BaseModel):
    """
    动作评价结果 Schema。

    类说明：
    保存 M3 评价函数对单个候选动作的评分结果，并补充 M4 的路径搜索惩罚项。
    """

    action: TrainingAction
    recovery: float
    fatigue: float
    training_benefit: float
    total_reward: float
    adjusted_reward: float
    next_fatigue_state: int
    explanation: str


class DailyPlan(BaseModel):
    """
    每日训练计划 Schema。

    类说明：
    表示动态规划输出路径中的一个阶段，包含第几天、训练动作、评分结果和推荐原因。
    """

    day_index: int
    day_label: str
    action_id: str
    training_name: str
    training_type: str
    intensity: str
    duration: float
    recovery: float
    fatigue: float
    training_benefit: float
    total_reward: float
    accumulated_reward: float
    reason: str


class PlannerRequest(BaseModel):
    """
    7 天训练计划请求 Schema。

    类说明：
    接口支持两种输入方式：传入 user_id 时由 M4 通过 M3 读取标准 AgentContext；
    传入 agent_context 时可直接用于实验或调试，不需要再访问数据库。
    """

    user_id: int | None = None
    agent_context: AgentContextSchema | None = None

    @model_validator(mode="after")
    def validate_source(self):
        """确保 user_id 和 agent_context 至少提供一个。"""

        if self.user_id is None and self.agent_context is None:
            raise ValueError("user_id or agent_context is required")
        return self


class WeeklyPlanResponse(BaseModel):
    """
    7 天最优训练计划响应 Schema。

    类说明：
    输出动态规划搜索得到的最优路径，用于前端展示和 Qwen2.5 解释生成。
    """

    user_id: int | None = None
    horizon_days: int = 7
    total_plan_reward: float
    initial_state: dict[str, Any]
    optimal_path: list[DailyPlan]
    decision_summary: str
