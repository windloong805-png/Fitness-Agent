"""
M1 用户画像模块 AgentContext 定义。

模块说明：
导出 AgentContext 结构，作为用户画像模块向 Agent 调度层、知识增强模块、动态规划模块传递上下文的标准格式。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计
"""

from backend.profile.schemas import AgentContext


__all__ = ["AgentContext"]
