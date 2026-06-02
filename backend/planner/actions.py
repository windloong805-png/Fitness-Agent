"""
M4 动态规划训练决策模块候选动作库。

模块说明：
本文件负责生成候选训练动作集合。动作库不直接计算最终收益，而是为 planner.py 提供可枚举动作，
再由 M3 训练收益评估函数计算奖励。

数据流说明：
AgentContext -> generate_candidate_actions() -> list[TrainingAction] -> 动态规划搜索。

论文映射说明：
对应模块：M4 动态规划训练决策模块
对应论文：第四章 4.3 动态规划训练决策模型设计
"""

from backend.reward.schemas import AgentContextSchema
from backend.planner.schemas import TrainingAction


def generate_candidate_actions(agent_context: AgentContextSchema | None = None) -> list[TrainingAction]:
    """
    生成候选训练动作集合。

    函数说明：
    动态规划的核心是“在每个阶段从候选动作中选择最优动作”。因此需要先定义一个有限、
    可解释、可扩展的动作集合。这里根据用户目标和健康限制做轻量过滤，避免明显不适合的训练进入搜索。

    输入参数：
    agent_context：可选的 M3 AgentContext。若传入，则根据 goal、constraints 调整动作集合。

    返回参数：
    list[TrainingAction]：候选训练动作列表。
    """

    actions = [
        TrainingAction(
            action_id="upper_strength",
            name="上肢力量训练",
            training_type="strength",
            intensity="medium",
            duration=45,
            goal_match_score=8,
            fatigue_delta=2.0,
            recovery_delta=0.0,
            reason="提升力量训练收益，适合增肌或减脂增肌目标。",
        ),
        TrainingAction(
            action_id="lower_strength",
            name="下肢力量训练",
            training_type="strength",
            intensity="medium",
            duration=50,
            goal_match_score=8,
            fatigue_delta=2.5,
            recovery_delta=0.0,
            reason="刺激大肌群，提升综合训练收益。",
        ),
        TrainingAction(
            action_id="cardio_base",
            name="中低强度有氧",
            training_type="cardio",
            intensity="medium",
            duration=40,
            goal_match_score=8,
            fatigue_delta=1.5,
            recovery_delta=0.0,
            reason="提高心肺能力和能量消耗，疲劳代价相对可控。",
        ),
        TrainingAction(
            action_id="hiit_fat_loss",
            name="HIIT 燃脂训练",
            training_type="hiit",
            intensity="high",
            duration=24,
            goal_match_score=9,
            fatigue_delta=3.5,
            recovery_delta=0.0,
            reason="单位时间收益较高，但需要较好的恢复状态支撑。",
        ),
        TrainingAction(
            action_id="core_mobility",
            name="核心稳定与灵活性",
            training_type="mobility",
            intensity="low",
            duration=30,
            goal_match_score=6.5,
            fatigue_delta=0.8,
            recovery_delta=0.5,
            reason="改善动作控制，降低后续训练风险。",
        ),
        TrainingAction(
            action_id="active_recovery",
            name="主动恢复",
            training_type="recovery",
            intensity="low",
            duration=25,
            goal_match_score=6,
            fatigue_delta=0.2,
            recovery_delta=1.8,
            reason="在疲劳较高时促进恢复，维持用户反馈闭环的连续性。",
        ),
    ]

    if agent_context is None:
        return actions

    constraints_text = " ".join(
        f"{item.get('constraint_type', '')} {item.get('description', '')} {item.get('severity', '')}"
        for item in agent_context.constraints
    ).lower()
    primary_goal = str(agent_context.goal.get("primary_goal") or "")

    filtered = actions
    if "膝" in constraints_text or "knee" in constraints_text:
        filtered = [action for action in filtered if action.action_id not in {"lower_strength", "hiit_fat_loss"}]

    if "减脂" in primary_goal or "fat" in primary_goal.lower():
        return _boost_goal_match(filtered, {"cardio_base": 9.0, "hiit_fat_loss": 9.5})

    if "增肌" in primary_goal or "strength" in primary_goal.lower():
        return _boost_goal_match(filtered, {"upper_strength": 9.0, "lower_strength": 9.0})

    return filtered


def _boost_goal_match(actions: list[TrainingAction], boosts: dict[str, float]) -> list[TrainingAction]:
    """
    根据用户目标调整候选动作的目标匹配分。

    函数说明：
    目标匹配分是 M3 training_benefit 的重要输入。这里不改变动作本身，只改变候选动作与目标的匹配程度。
    """

    boosted = []
    for action in actions:
        if action.action_id in boosts:
            boosted.append(action.model_copy(update={"goal_match_score": boosts[action.action_id]}))
        else:
            boosted.append(action)
    return boosted
