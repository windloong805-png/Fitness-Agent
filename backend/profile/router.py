"""
M1 用户画像模块 FastAPI 路由。

模块说明：
提供用户画像查询、创建、更新接口，是前端、Agent 调度层与用户画像模块交互的 HTTP 入口。

论文映射说明：
对应模块：M1 用户画像模块
对应论文：第四章 系统设计；用户画像模型设计；第六章 系统实现
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.profile.schemas import ProfileCreate, ProfileRead, ProfileUpdate
from backend.profile.service import create_profile, get_profile, update_profile


router = APIRouter(prefix="/api/profile", tags=["M1 用户画像模块"])


@router.get("/{user_id}", response_model=ProfileRead)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户画像接口。

    函数说明：
    GET /api/profile/{user_id}，返回完整用户画像和 AgentContext。
    """

    return get_profile(db, user_id)


@router.post("", response_model=ProfileRead, status_code=201)
def create_user_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    """
    创建用户画像接口。

    函数说明：
    POST /api/profile，创建用户基础信息、目标、每日状态、限制和偏好。
    """

    return create_profile(db, payload)


@router.put("/{user_id}", response_model=ProfileRead)
def update_user_profile(user_id: int, payload: ProfileUpdate, db: Session = Depends(get_db)):
    """
    更新用户画像接口。

    函数说明：
    PUT /api/profile/{user_id}，局部更新指定用户画像，并返回最新 AgentContext。
    """

    return update_profile(db, user_id, payload)
