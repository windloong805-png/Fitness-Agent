"""
M1 用户画像模块 Pydantic Schema。

模块说明：
定义用户画像接口的请求、响应和 AgentContext 数据结构。Schema 字段与 ORM 模型保持一致，
作为 M1 用户画像模块的数据契约标准。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """用户基础信息 Schema。"""

    username: str = Field(..., min_length=1, max_length=64)
    nickname: str | None = None
    phone: str | None = None


class UserCreate(UserBase):
    """创建用户基础信息请求 Schema。"""


class UserUpdate(BaseModel):
    """更新用户基础信息请求 Schema。"""

    username: str | None = Field(default=None, min_length=1, max_length=64)
    nickname: str | None = None
    phone: str | None = None


class UserRead(UserBase):
    """用户基础信息响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserProfileBase(BaseModel):
    """用户长期画像 Schema。"""

    gender: str | None = None
    age: int | None = Field(default=None, ge=0, le=120)
    height_cm: float | None = Field(default=None, gt=0)
    weight_kg: float | None = Field(default=None, gt=0)
    training_level: str | None = None
    occupation: str | None = None


class UserProfileRead(UserProfileBase):
    """用户长期画像响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserGoalBase(BaseModel):
    """用户训练目标 Schema。"""

    primary_goal: str
    target_weight_kg: float | None = Field(default=None, gt=0)
    weekly_training_days: int | None = Field(default=None, ge=0, le=7)
    target_date: date | None = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)


class UserGoalRead(UserGoalBase):
    """用户训练目标响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserGoalUpdate(BaseModel):
    """更新用户训练目标请求 Schema。"""

    primary_goal: str | None = None
    target_weight_kg: float | None = Field(default=None, gt=0)
    weekly_training_days: int | None = Field(default=None, ge=0, le=7)
    target_date: date | None = None
    progress: float | None = Field(default=None, ge=0.0, le=100.0)


class DailyStatusBase(BaseModel):
    """用户每日动态状态 Schema。"""

    status_date: date | None = None
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    recovery_score: float | None = Field(default=None, ge=0, le=100)
    fatigue_score: float | None = Field(default=None, ge=0, le=100)
    soreness_level: float | None = Field(default=None, ge=0, le=10)
    rpe: float | None = Field(default=None, ge=0, le=10)
    note: str | None = None


class DailyStatusRead(DailyStatusBase):
    """用户每日动态状态响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserConstraintBase(BaseModel):
    """用户健康限制 Schema。"""

    constraint_type: str
    description: str
    severity: str = "medium"


class UserConstraintRead(UserConstraintBase):
    """用户健康限制响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class UserPreferenceBase(BaseModel):
    """用户训练偏好 Schema。"""

    preference_type: str
    value: str
    weight: float = Field(default=1.0, ge=0.0)


class UserPreferenceRead(UserPreferenceBase):
    """用户训练偏好响应 Schema。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class ProfileCreate(BaseModel):
    """
    创建完整用户画像请求 Schema。

    函数说明：
    用于 POST /api/profile，一次性创建用户、长期画像、训练目标、每日状态、约束和偏好。
    """

    user: UserCreate
    profile: UserProfileBase | None = None
    goal: UserGoalBase | None = None
    daily_status: DailyStatusBase | None = None
    constraints: list[UserConstraintBase] = Field(default_factory=list)
    preferences: list[UserPreferenceBase] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    """
    更新完整用户画像请求 Schema。

    函数说明：
    用于 PUT /api/profile/{user_id}，支持局部更新用户画像信息。
    """

    user: UserUpdate | None = None
    profile: UserProfileBase | None = None
    goal: UserGoalUpdate | None = None
    daily_status: DailyStatusBase | None = None
    constraints: list[UserConstraintBase] | None = None
    preferences: list[UserPreferenceBase] | None = None


class ComputedState(BaseModel):
    """AgentContext 中的计算状态 Schema。"""

    bmi: float | None = None
    recovery: float
    fatigue: float
    goal_progress: float


class AgentContext(BaseModel):
    """供 Agent 调度层使用的用户画像上下文 Schema。"""

    profile: dict[str, Any]
    goal: dict[str, Any]
    daily_status: dict[str, Any]
    constraints: list[dict[str, Any]]
    preferences: list[dict[str, Any]]
    computed_state: ComputedState


class ProfileRead(BaseModel):
    """完整用户画像响应 Schema。"""

    user: UserRead
    profile: UserProfileRead | None = None
    goal: UserGoalRead | None = None
    daily_status: DailyStatusRead | None = None
    constraints: list[UserConstraintRead] = Field(default_factory=list)
    preferences: list[UserPreferenceRead] = Field(default_factory=list)
    agent_context: AgentContext
