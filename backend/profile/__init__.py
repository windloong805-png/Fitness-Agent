"""
M1 用户画像模块。

模块说明：
负责维护用户基础信息、训练目标、每日状态、健康限制与训练偏好，并构建 AgentContext。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计
"""

from backend.profile.context import AgentContext
from backend.profile.service import (
    build_agent_context,
    create_profile,
    get_profile,
    update_profile,
)

__all__ = [
    "AgentContext",
    "build_agent_context",
    "create_profile",
    "get_profile",
    "update_profile",
]
