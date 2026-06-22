import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Tag, User
from app.schemas.tag import TagCreate, TagUpdate, TagResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag).where(Tag.user_id == current_user.id).order_by(Tag.name)
    )
    return result.scalars().all()


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    req: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = Tag(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        color=req.color,
    )
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: uuid.UUID,
    req: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if req.name is not None:
        tag.name = req.name
    if req.color is not None:
        tag.color = req.color
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
    return None
