"""
M3 训练收益评估模块。

模块说明：
本包负责计算恢复指数 Recovery、疲劳指数 Fatigue、训练收益 TrainingBenefit 和综合收益 TotalReward。
M3 位于 M1 用户画像模块与 M4 动态规划模块之间：它读取 AgentContext 中的用户状态，
输出可计算、可解释的奖励信号，供动态规划搜索训练路径，也供 Qwen2.5 生成推荐理由。

数据流说明：
M1 用户画像模块 -> AgentContext -> M3 训练收益评估 -> RewardOutput / Reward AgentContext -> M4 动态规划模块与 M5 Qwen 交互模块。

论文映射说明：
对应模块：M3 训练收益评估模块
对应论文：第四章 4.2 训练收益评估模型设计
"""

from backend.reward.calculator import build_reward_context, calculate_reward
from backend.reward.formulas import (
    calculate_fatigue,
    calculate_recovery,
    calculate_total_reward,
    calculate_training_benefit,
)
from backend.reward.schemas import AgentContextSchema, RewardInput, RewardOutput, RewardWeights

__all__ = [
    "AgentContextSchema",
    "RewardInput",
    "RewardOutput",
    "RewardWeights",
    "build_reward_context",
    "calculate_fatigue",
    "calculate_recovery",
    "calculate_reward",
    "calculate_total_reward",
    "calculate_training_benefit",
]
