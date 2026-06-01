"""
M1 用户画像模块 ORM 模型。

模块说明：
定义 User、UserProfile、UserGoal、DailyStatus、UserConstraint、UserPreference 六类 SQLAlchemy 模型。
数据库表结构以本文件定义为标准，MySQL 数据库 fitness_agent 应跟随本模型重建或迁移。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计
"""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    """
    用户基础表。

    函数说明：
    保存用户账号级基础信息，是用户画像模块的聚合根。
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    profile: Mapped["UserProfile"] = relationship(back_populates="user", cascade="all, delete-orphan")
    goal: Mapped["UserGoal"] = relationship(back_populates="user", cascade="all, delete-orphan")
    daily_statuses: Mapped[list["DailyStatus"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="DailyStatus.status_date.desc()",
    )
    constraints: Mapped[list["UserConstraint"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    preferences: Mapped[list["UserPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    """
    用户长期画像表。

    函数说明：
    保存身高、体重、训练水平等长期稳定特征。
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, index=True)
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    training_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(64), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="profile")


class UserGoal(Base):
    """
    用户训练目标表。

    函数说明：
    保存当前阶段目标、目标体重、周训练频次和目标进度。
    """

    __tablename__ = "user_goals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, index=True)
    primary_goal: Mapped[str] = mapped_column(String(64))
    target_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    weekly_training_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="goal")


class DailyStatus(Base):
    """
    用户每日动态状态表。

    函数说明：
    保存睡眠、恢复、疲劳、疼痛和主观 RPE 等动态状态，用于构建当日 AgentContext。
    """

    __tablename__ = "daily_statuses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    status_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    recovery_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fatigue_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    soreness_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    rpe: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="daily_statuses")


class UserConstraint(Base):
    """
    用户健康限制表。

    函数说明：
    保存伤病、禁忌动作、训练风险和其他安全约束，供 RAG 与动态规划模块共同使用。
    """

    __tablename__ = "user_constraints"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    constraint_type: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="constraints")


class UserPreference(Base):
    """
    用户训练偏好表。

    函数说明：
    保存用户偏好的训练类型、器械、时间段和训练场景，提高推荐可采纳性。
    """

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    preference_type: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(String(128))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="preferences")
