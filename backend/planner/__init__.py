"""
M4 动态规划训练决策模块。

模块说明：
本包负责根据 M1 用户画像与 M3 训练收益评估结果，生成未来 7 天训练计划。
M4 不直接跨模块读取数据库，而是优先使用 AgentContext；当传入 user_id 时，由 planner.py 调用 M3
的 build_reward_context() 获取标准上下文。

数据流说明：
M1 用户画像 -> M3 Reward AgentContext -> M4 候选动作生成 -> 动态规划搜索 -> 7 天训练计划。

论文映射说明：
对应模块：M4 动态规划训练决策模块
对应论文：第四章 4.3 动态规划训练决策模型设计
"""

from backend.planner.actions import generate_candidate_actions
from backend.planner.planner import evaluate_action_reward, plan_weekly_training
from backend.planner.schemas import PlannerRequest, WeeklyPlanResponse

__all__ = [
    "PlannerRequest",
    "WeeklyPlanResponse",
    "evaluate_action_reward",
    "generate_candidate_actions",
    "plan_weekly_training",
]
