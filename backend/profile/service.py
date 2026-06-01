"""
M1 用户画像模块业务服务。

模块说明：
实现用户画像创建、更新、查询和 AgentContext 构建逻辑，是 API 层与 ORM 模型之间的业务边界。
服务层以 M1 ORM 模型和 Schema 为标准，不迁就数据库中旧有的临时表结构。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计
"""

from datetime import date
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

import backend.profile.models as models
from backend.profile.schemas import AgentContext, ComputedState, ProfileCreate, ProfileRead, ProfileUpdate


def create_profile(db: Session, payload: ProfileCreate) -> ProfileRead:
    """
    创建用户画像。

    函数说明：
    根据提交数据创建用户基础信息、长期画像、训练目标、当日状态、健康限制和训练偏好。
    """

    existing_user = db.query(models.User).filter(models.User.username == payload.user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="username already exists")

    user = models.User(**payload.user.model_dump())
    db.add(user)
    db.flush()

    if payload.profile:
        db.add(models.UserProfile(user_id=user.id, **payload.profile.model_dump()))

    if payload.goal:
        db.add(models.UserGoal(user_id=user.id, **payload.goal.model_dump()))

    if payload.daily_status:
        status_data = payload.daily_status.model_dump()
        status_data["status_date"] = status_data["status_date"] or date.today()
        db.add(models.DailyStatus(user_id=user.id, **status_data))

    for item in payload.constraints:
        db.add(models.UserConstraint(user_id=user.id, **item.model_dump()))

    for item in payload.preferences:
        db.add(models.UserPreference(user_id=user.id, **item.model_dump()))

    db.commit()
    return get_profile(db, user.id)


def update_profile(db: Session, user_id: int, payload: ProfileUpdate) -> ProfileRead:
    """
    更新用户画像。

    函数说明：
    对指定用户执行局部更新。constraints 和 preferences 采用整体替换策略，daily_status 新增一条每日状态记录。
    """

    user = _get_user_or_404(db, user_id)

    if payload.user:
        for key, value in payload.user.model_dump(exclude_unset=True).items():
            setattr(user, key, value)

    if payload.profile:
        if not user.profile:
            user.profile = models.UserProfile(user_id=user.id)
        for key, value in payload.profile.model_dump(exclude_unset=True).items():
            setattr(user.profile, key, value)

    if payload.goal:
        if not user.goal:
            user.goal = models.UserGoal(user_id=user.id, primary_goal=payload.goal.primary_goal or "未设置")
        for key, value in payload.goal.model_dump(exclude_unset=True).items():
            setattr(user.goal, key, value)

    if payload.daily_status:
        status_data = payload.daily_status.model_dump(exclude_unset=True)
        status_data["status_date"] = status_data.get("status_date") or date.today()
        db.add(models.DailyStatus(user_id=user.id, **status_data))

    if payload.constraints is not None:
        user.constraints.clear()
        for item in payload.constraints:
            user.constraints.append(models.UserConstraint(**item.model_dump()))

    if payload.preferences is not None:
        user.preferences.clear()
        for item in payload.preferences:
            user.preferences.append(models.UserPreference(**item.model_dump()))

    db.commit()
    return get_profile(db, user.id)


def get_profile(db: Session, user_id: int) -> ProfileRead:
    """
    查询用户画像。

    函数说明：
    按用户 ID 返回完整画像，并同步构建 AgentContext，供前端展示或 Agent 调度层调用。
    """

    user = _get_user_or_404(db, user_id)
    daily_status = user.daily_statuses[0] if user.daily_statuses else None
    agent_context = build_agent_context(user)

    return ProfileRead(
        user=user,
        profile=user.profile,
        goal=user.goal,
        daily_status=daily_status,
        constraints=user.constraints,
        preferences=user.preferences,
        agent_context=agent_context,
    )


def build_agent_context(user: models.User) -> AgentContext:
    """
    构建 AgentContext。

    函数说明：
    将用户长期画像、目标、最新每日状态、健康限制与训练偏好整合为智能体调度层可直接使用的上下文结构。
    """

    latest_status = user.daily_statuses[0] if user.daily_statuses else None

    profile = _model_to_dict(
        user.profile,
        include=["gender", "age", "height_cm", "weight_kg", "training_level", "occupation"],
    )
    goal = _model_to_dict(
        user.goal,
        include=["primary_goal", "target_weight_kg", "weekly_training_days", "target_date", "progress"],
    )
    daily_status = _model_to_dict(
        latest_status,
        include=["status_date", "sleep_hours", "recovery_score", "fatigue_score", "soreness_level", "rpe", "note"],
    )

    constraints = [
        _model_to_dict(item, include=["constraint_type", "description", "severity"]) for item in user.constraints
    ]
    preferences = [
        _model_to_dict(item, include=["preference_type", "value", "weight"]) for item in user.preferences
    ]

    computed_state = ComputedState(
        bmi=_calculate_bmi(profile.get("height_cm"), profile.get("weight_kg")),
        recovery=_normalize_score(daily_status.get("recovery_score"), default=70.0),
        fatigue=_normalize_score(daily_status.get("fatigue_score"), default=30.0),
        goal_progress=_normalize_score(goal.get("progress"), default=0.0),
    )

    return AgentContext(
        profile=profile,
        goal=goal,
        daily_status=daily_status,
        constraints=constraints,
        preferences=preferences,
        computed_state=computed_state,
    )


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    """
    获取用户聚合根。

    函数说明：
    统一加载用户画像相关关系，若用户不存在则返回 404。
    """

    user = (
        db.query(models.User)
        .options(
            selectinload(models.User.profile),
            selectinload(models.User.goal),
            selectinload(models.User.daily_statuses),
            selectinload(models.User.constraints),
            selectinload(models.User.preferences),
        )
        .filter(models.User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    return user


def _model_to_dict(model: Any, include: list[str]) -> dict[str, Any]:
    """
    ORM 模型转字典。

    函数说明：
    只导出 AgentContext 需要的字段，避免泄露数据库内部字段。
    """

    if model is None:
        return {}
    return {key: getattr(model, key) for key in include}


def _calculate_bmi(height_cm: float | None, weight_kg: float | None) -> float | None:
    """
    计算 BMI。

    函数说明：
    根据身高和体重计算 BMI，作为 computed_state 的基础体征指标。
    """

    if not height_cm or not weight_kg:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 2)


def _normalize_score(value: float | None, default: float) -> float:
    """
    标准化评分。

    函数说明：
    将恢复、疲劳和目标进度限制在 0 到 100 区间，缺失时使用默认值。
    """

    score = default if value is None else value
    return max(0.0, min(100.0, float(score)))
