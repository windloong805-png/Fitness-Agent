"""
M4 动态规划训练决策模块核心算法。

模块说明：
本文件实现候选动作生成、动作收益评估和 7 天训练计划生成。
动态规划的设计思想是：把未来 7 天视为 7 个决策阶段，每天从候选训练动作中选择一个动作，
状态变量使用疲劳桶表示，目标是在控制疲劳的前提下最大化累计训练收益。

数据流说明：
user_id 或 AgentContext -> M3 Reward AgentContext -> candidate actions -> DP state transition -> WeeklyPlanResponse。

论文映射说明：
对应模块：M4 动态规划训练决策模块
对应论文：第四章 4.3 动态规划训练决策模型设计
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.planner.actions import generate_candidate_actions
from backend.planner.schemas import ActionEvaluation, DailyPlan, TrainingAction, WeeklyPlanResponse
from backend.reward.calculator import build_reward_context, calculate_reward
from backend.reward.schemas import AgentContextSchema, RewardInput


HORIZON_DAYS = 7
DAY_LABELS = ["第1天", "第2天", "第3天", "第4天", "第5天", "第6天", "第7天"]


@dataclass
class _DPState:
    """动态规划内部状态，保存累计收益和路径。"""

    reward: float
    path: list[DailyPlan]


def evaluate_action_reward(
    action: TrainingAction,
    agent_context: AgentContextSchema,
    fatigue_state: int | None = None,
    previous_action: TrainingAction | None = None,
) -> ActionEvaluation:
    """
    评价单个候选训练动作。

    函数说明：
    该函数是 M4 与 M3 的连接点。M4 不重新发明收益公式，而是调用 M3 的 calculate_reward()；
    然后 M4 再加入动态规划需要的路径惩罚，例如疲劳状态过高和连续高强度训练惩罚。

    输入参数：
    action：候选训练动作。
    agent_context：M3 Reward AgentContext，包含 M1 用户画像和 M3 computed_state。
    fatigue_state：当前动态规划疲劳桶，0~10。
    previous_action：前一天动作，用于避免连续高强度训练。

    返回参数：
    ActionEvaluation：包含 M3 原始收益、M4 调整收益和下一疲劳状态。

    对应模块：
    M4 动态规划训练决策模块。

    对应论文：
    第四章 4.3 动态规划训练决策模型设计。
    """

    current_fatigue = float(fatigue_state if fatigue_state is not None else agent_context.computed_state.fatigue)
    reward_output = calculate_reward(
        RewardInput(
            sleep_hours=agent_context.daily_status.get("sleep_hours"),
            sleep_quality_score=None,
            current_fatigue_score=current_fatigue,
            stress_score=3.0,
            training_load=current_fatigue,
            soreness_count=agent_context.daily_status.get("soreness_level"),
            training_type=action.training_type,
            intensity=action.intensity,
            duration=action.duration,
            goal_match_score=action.goal_match_score,
        )
    )

    next_fatigue = _next_fatigue_state(current_fatigue, action)
    penalty = _path_penalty(action, current_fatigue, previous_action)
    adjusted_reward = round(max(reward_output.total_reward - penalty, 0.0), 2)

    return ActionEvaluation(
        action=action,
        recovery=reward_output.recovery,
        fatigue=reward_output.fatigue,
        training_benefit=reward_output.training_benefit,
        total_reward=reward_output.total_reward,
        adjusted_reward=adjusted_reward,
        next_fatigue_state=next_fatigue,
        explanation=_build_action_explanation(action, reward_output.total_reward, penalty, next_fatigue),
    )


def plan_weekly_training(
    user_id: int | None = None,
    agent_context: AgentContextSchema | None = None,
    db: Session | None = None,
) -> WeeklyPlanResponse:
    """
    生成未来 7 天训练计划。

    函数说明：
    该函数实现 M4 的核心动态规划流程。若传入 user_id，则先调用 M3 的 build_reward_context()
    读取 M1 用户画像和 M3 评估上下文；若直接传入 agent_context，则用于实验或接口调试。

    输入参数：
    user_id：可选用户 ID。
    agent_context：可选 M3 AgentContext。
    db：可选数据库会话。

    返回参数：
    WeeklyPlanResponse：7 天最优训练计划 JSON。

    对应模块：
    M4 动态规划训练决策模块。

    对应论文：
    第四章 4.3 动态规划训练决策模型设计。
    """

    if agent_context is None:
        if user_id is None:
            raise ValueError("user_id or agent_context is required")
        if db is None:
            with SessionLocal() as local_db:
                agent_context = build_reward_context(user_id=user_id, db=local_db)
        else:
            agent_context = build_reward_context(user_id=user_id, db=db)

    actions = generate_candidate_actions(agent_context)
    initial_fatigue = _state_bucket(agent_context.computed_state.fatigue)
    dp: dict[int, _DPState] = {initial_fatigue: _DPState(reward=0.0, path=[])}

    for day_index in range(1, HORIZON_DAYS + 1):
        next_dp: dict[int, _DPState] = {}
        for fatigue_state, state in dp.items():
            previous_action = _previous_action_from_path(state.path, actions)
            for action in actions:
                evaluation = evaluate_action_reward(action, agent_context, fatigue_state, previous_action)
                accumulated = round(state.reward + evaluation.adjusted_reward, 2)
                daily_plan = DailyPlan(
                    day_index=day_index,
                    day_label=DAY_LABELS[day_index - 1],
                    action_id=action.action_id,
                    training_name=action.name,
                    training_type=action.training_type,
                    intensity=action.intensity,
                    duration=action.duration,
                    recovery=evaluation.recovery,
                    fatigue=evaluation.fatigue,
                    training_benefit=evaluation.training_benefit,
                    total_reward=evaluation.adjusted_reward,
                    accumulated_reward=accumulated,
                    reason=evaluation.explanation,
                )
                old = next_dp.get(evaluation.next_fatigue_state)
                if old is None or accumulated > old.reward:
                    next_dp[evaluation.next_fatigue_state] = _DPState(
                        reward=accumulated,
                        path=[*state.path, daily_plan],
                    )
        dp = _keep_top_states(next_dp, limit=12)

    best_state = max(dp.values(), key=lambda item: item.reward)
    return WeeklyPlanResponse(
        user_id=user_id,
        horizon_days=HORIZON_DAYS,
        total_plan_reward=round(best_state.reward, 2),
        initial_state={
            "fatigue_state": initial_fatigue,
            "bmi": agent_context.computed_state.bmi,
            "recovery": agent_context.computed_state.recovery,
            "fatigue": agent_context.computed_state.fatigue,
        },
        optimal_path=best_state.path,
        decision_summary=(
            "动态规划以 7 天为决策阶段，以疲劳桶为状态变量，"
            "在候选训练动作中搜索累计综合收益最高且疲劳可控的训练路径。"
        ),
    )


def _next_fatigue_state(current_fatigue: float, action: TrainingAction) -> int:
    """根据当前疲劳状态和动作疲劳影响计算下一状态。"""

    next_value = current_fatigue + action.fatigue_delta - action.recovery_delta
    if action.training_type == "recovery":
        next_value -= 0.8
    return _state_bucket(next_value)


def _path_penalty(action: TrainingAction, fatigue_state: float, previous_action: TrainingAction | None) -> float:
    """计算路径惩罚，避免疲劳过高或连续高强度训练。"""

    penalty = 0.0
    if fatigue_state >= 7 and action.intensity in {"medium", "high"}:
        penalty += 1.5
    if fatigue_state >= 8 and action.intensity == "high":
        penalty += 2.0
    if previous_action and previous_action.intensity == "high" and action.intensity == "high":
        penalty += 1.2
    if previous_action and previous_action.training_type == action.training_type and action.training_type != "recovery":
        penalty += 0.4
    return penalty


def _build_action_explanation(action: TrainingAction, total_reward: float, penalty: float, next_fatigue: int) -> str:
    """生成给 Qwen2.5 或前端展示的动作选择解释。"""

    if penalty > 0:
        return (
            f"{action.reason} M3 原始综合收益为 {total_reward}，"
            f"M4 根据疲劳状态加入 {penalty} 的路径惩罚，下一疲劳状态约为 {next_fatigue}。"
        )
    return f"{action.reason} M3 综合收益为 {total_reward}，下一疲劳状态约为 {next_fatigue}。"


def _previous_action_from_path(path: list[DailyPlan], actions: list[TrainingAction]) -> TrainingAction | None:
    """从已有路径中找到前一天动作，供连续动作惩罚使用。"""

    if not path:
        return None
    action_map = {action.action_id: action for action in actions}
    return action_map.get(path[-1].action_id)


def _keep_top_states(states: dict[int, _DPState], limit: int) -> dict[int, _DPState]:
    """保留收益较高的状态，控制搜索规模。"""

    ranked = sorted(states.items(), key=lambda item: item[1].reward, reverse=True)
    return dict(ranked[:limit])


def _state_bucket(value: float) -> int:
    """将连续疲劳值离散为 0~10 的状态桶，便于动态规划转移。"""

    return max(0, min(10, round(float(value))))
