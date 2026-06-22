import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Category, User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .where(Category.user_id == current_user.id)
        .order_by(Category.sort_order)
    )
    categories = result.scalars().all()
    cat_map = {c.id: CategoryResponse.model_validate(c) for c in categories}
    roots = []
    for cat in cat_map.values():
        if cat.parent_id and cat.parent_id in cat_map:
            parent = cat_map[cat.parent_id]
            parent.children.append(cat)
        else:
            roots.append(cat)
    return roots


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    req: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category = Category(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=req.name,
        parent_id=req.parent_id,
        sort_order=req.sort_order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    req: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == current_user.id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if req.name is not None:
        category.name = req.name
    if req.parent_id is not None:
        category.parent_id = req.parent_id
    if req.sort_order is not None:
        category.sort_order = req.sort_order
    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == current_user.id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    return None
