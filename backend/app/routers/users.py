import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, ApiConfig
from app.schemas.user import (
    UserResponse, UpdateUserRequest,
    ApiConfigCreate, ApiConfigUpdate, ApiConfigResponse,
)
from app.dependencies import get_current_user
from app.security import encrypt_api_key

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    req: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.username is not None:
        current_user.username = req.username
    if req.email is not None:
        current_user.email = req.email
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.get("/api-configs", response_model=list[ApiConfigResponse])
async def list_api_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.user_id == current_user.id, ApiConfig.is_active == True)
    )
    return result.scalars().all()


@router.get("/api-configs/global", response_model=list[ApiConfigResponse])
async def list_global_api_configs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.user_id.is_(None), ApiConfig.is_active == True)
    )
    return result.scalars().all()


@router.post("/api-configs", response_model=ApiConfigResponse, status_code=201)
async def create_api_config(
    req: ApiConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    config = ApiConfig(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        api_base=req.api_base.rstrip("/"),
        api_key_encrypted=encrypt_api_key(req.api_key),
        default_model=req.default_model,
    )
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


@router.put("/api-configs/{config_id}", response_model=ApiConfigResponse)
async def update_api_config(
    config_id: uuid.UUID,
    req: ApiConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id, ApiConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(404, "API config not found")
    if req.name is not None:
        config.name = req.name
    if req.api_base is not None:
        config.api_base = req.api_base.rstrip("/")
    if req.api_key is not None:
        config.api_key_encrypted = encrypt_api_key(req.api_key)
    if req.default_model is not None:
        config.default_model = req.default_model
    await db.flush()
    await db.refresh(config)
    return config


@router.delete("/api-configs/{config_id}", status_code=204)
async def delete_api_config(
    config_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ApiConfig).where(ApiConfig.id == config_id, ApiConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(404, "API config not found")
    await db.delete(config)
    return None
