"""
M3 训练收益评估模块公式层。

模块说明：
本文件只保存可复用的纯计算公式，不读取数据库，也不依赖 FastAPI。
这样设计是为了让 M4 动态规划模块可以在大量候选训练动作上快速调用评价函数，
也方便论文实验章节单独对公式权重进行对比实验。

数据流说明：
数值输入 -> 归一化 -> Recovery / Fatigue / TrainingBenefit / TotalReward。

论文映射说明：
对应模块：M3 训练收益评估模块
对应论文：第四章 4.2 训练收益评估模型设计
"""

from __future__ import annotations


DEFAULT_REWARD_WEIGHTS = {
    "w1": 0.5,
    "w2": 0.3,
    "w3": 0.2,
}

INTENSITY_SCORE_MAP = {
    "low": 3.0,
    "轻": 3.0,
    "低": 3.0,
    "medium": 6.0,
    "moderate": 6.0,
    "中": 6.0,
    "中等": 6.0,
    "high": 8.0,
    "高": 8.0,
    "较高": 8.0,
}

TRAINING_TYPE_BASE_SCORE = {
    "strength": 8.0,
    "力量": 8.0,
    "cardio": 7.5,
    "有氧": 7.5,
    "hiit": 8.0,
    "mobility": 6.5,
    "拉伸": 6.5,
    "recovery": 6.0,
    "恢复": 6.0,
}


def calculate_recovery(
    sleep_hours: float | None,
    sleep_quality_score: float | None,
    fatigue_score: float | None,
    stress_score: float | None,
) -> float:
    """
    计算恢复指数 Recovery。

    函数说明：
    恢复指数用于估计用户今天是否适合训练。设计上同时考虑睡眠时长、睡眠质量、疲劳和压力，
    因为健身推荐不能只看训练目标，还必须考虑身体是否具备承受训练刺激的状态。

    输入参数：
    sleep_hours：睡眠时长，建议范围 0~24。
    sleep_quality_score：睡眠质量，支持 0~10 或 0~100。
    fatigue_score：已有疲劳评分，支持 0~10 或 0~100。
    stress_score：压力评分，支持 0~10 或 0~100。

    返回参数：
    recovery：0~10，值越高代表越适合训练。
    """

    sleep_duration_score = _score_sleep_duration(sleep_hours)
    sleep_quality = _to_ten_scale(sleep_quality_score, default=6.0)
    fatigue = _to_ten_scale(fatigue_score, default=3.0)
    stress = _to_ten_scale(stress_score, default=3.0)

    recovery = (
        0.40 * sleep_duration_score
        + 0.30 * sleep_quality
        + 0.20 * (10.0 - fatigue)
        + 0.10 * (10.0 - stress)
    )
    return _round_score(recovery)


def calculate_fatigue(
    training_load: float | None,
    soreness_count: float | None,
    stress_score: float | None,
) -> float:
    """
    计算疲劳指数 Fatigue。

    函数说明：
    疲劳指数用于估计用户是否需要恢复。训练负荷代表身体受到的训练刺激，
    酸痛数量代表局部肌群恢复压力，压力评分代表非训练因素对恢复的影响。

    输入参数：
    training_load：近期训练负荷，支持 0~10 或 0~100。
    soreness_count：酸痛部位数量，按 0~5 归一化。
    stress_score：压力评分，支持 0~10 或 0~100。

    返回参数：
    fatigue：0~10，值越高代表越需要恢复。
    """

    load = _to_ten_scale(training_load, default=4.0)
    soreness = _clamp((soreness_count or 0.0) / 5.0 * 10.0, 0.0, 10.0)
    stress = _to_ten_scale(stress_score, default=3.0)

    fatigue = 0.50 * load + 0.30 * soreness + 0.20 * stress
    return _round_score(fatigue)


def calculate_training_benefit(
    training_type: str | None,
    intensity: str | float | int | None,
    duration: float | None,
    goal_match_score: float | None,
) -> float:
    """
    计算训练收益 TrainingBenefit。

    函数说明：
    训练收益用于评估某次训练是否值得安排。它不直接代表“越累越好”，
    而是综合训练类型、强度、时长和用户目标匹配程度，评估本次训练对目标的有效贡献。

    输入参数：
    training_type：训练类型，例如 strength、cardio、hiit、力量、有氧。
    intensity：训练强度，支持 low/medium/high、中文强度或 0~10 数值。
    duration：预计训练时长，单位分钟。
    goal_match_score：与用户当前目标的匹配分，支持 0~10 或 0~100。

    返回参数：
    training_benefit：0~10，用于评估本次训练价值。
    """

    type_score = _training_type_score(training_type)
    intensity_score = _intensity_score(intensity)
    duration_score = _duration_score(duration)
    goal_match = _to_ten_scale(goal_match_score, default=7.0)

    benefit = 0.10 * type_score + 0.35 * intensity_score + 0.25 * duration_score + 0.30 * goal_match
    return _round_score(benefit)


def calculate_total_reward(
    recovery: float,
    fatigue: float,
    training_benefit: float,
    w1: float = DEFAULT_REWARD_WEIGHTS["w1"],
    w2: float = DEFAULT_REWARD_WEIGHTS["w2"],
    w3: float = DEFAULT_REWARD_WEIGHTS["w3"],
) -> float:
    """
    计算综合收益 TotalReward。

    函数说明：
    综合收益是提供给 M4 动态规划模块的评价函数核心。
    公式保留可配置权重，便于后续在论文实验中比较不同权重策略对计划推荐结果的影响。

    公式：
    total_reward = w1 * training_benefit + w2 * recovery - w3 * fatigue

    返回参数：
    total_reward：默认裁剪到 0~10，值越高代表越值得安排该训练。
    """

    reward = w1 * training_benefit + w2 * recovery - w3 * fatigue
    return _round_score(reward)


def _score_sleep_duration(sleep_hours: float | None) -> float:
    """将睡眠时长映射到 0~10。7.5 小时左右视为较优恢复窗口。"""

    if sleep_hours is None:
        return 6.0
    if sleep_hours <= 0:
        return 0.0
    if sleep_hours <= 7.5:
        return _clamp(sleep_hours / 7.5 * 10.0, 0.0, 10.0)
    if sleep_hours <= 9.0:
        return 10.0
    return _clamp(10.0 - (sleep_hours - 9.0) * 1.5, 6.0, 10.0)


def _to_ten_scale(value: float | int | None, default: float) -> float:
    """将 0~100 或 0~10 的输入统一转换为 0~10。"""

    if value is None:
        return default
    number = float(value)
    if number > 10:
        number = number / 10.0
    return _clamp(number, 0.0, 10.0)


def _intensity_score(intensity: str | float | int | None) -> float:
    """将训练强度转换为 0~10 分值，支持中文、英文和数值。"""

    if intensity is None:
        return 6.0
    if isinstance(intensity, (int, float)):
        return _to_ten_scale(intensity, default=6.0)
    return INTENSITY_SCORE_MAP.get(str(intensity).strip().lower(), 6.0)


def _training_type_score(training_type: str | None) -> float:
    """给常见训练类型一个基础收益分，未知类型使用中性偏高分。"""

    if not training_type:
        return 7.0
    return TRAINING_TYPE_BASE_SCORE.get(str(training_type).strip().lower(), 7.0)


def _duration_score(duration: float | None) -> float:
    """将训练时长映射为收益分。45~75 分钟通常具备较好收益，过短或过长都降低价值。"""

    if duration is None:
        return 7.0
    minutes = max(float(duration), 0.0)
    if minutes <= 45:
        return _clamp(minutes / 45.0 * 8.0, 0.0, 8.0)
    if minutes <= 75:
        return 9.0
    return _clamp(9.0 - (minutes - 75.0) / 30.0 * 2.0, 5.0, 9.0)


def _round_score(value: float) -> float:
    """裁剪到 0~10 并保留两位小数，便于前端展示和论文实验记录。"""

    return round(_clamp(value, 0.0, 10.0), 2)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """限制数值范围，避免异常输入破坏奖励函数。"""

    return max(minimum, min(maximum, value))
