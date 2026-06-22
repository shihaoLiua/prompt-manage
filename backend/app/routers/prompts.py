import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Prompt, PromptVersion, Tag, User
from app.schemas.prompt import (
    PromptCreate, PromptUpdate, PromptResponse, PromptListItem,
    PromptVersionResponse, PromptVersionCreate,
    ToggleFavoriteResponse, SetRatingRequest,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("", response_model=dict)
async def list_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[uuid.UUID] = Query(None),
    tag_id: Optional[uuid.UUID] = Query(None),
    is_favorite: Optional[bool] = Query(None),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Prompt).where(Prompt.user_id == current_user.id)

    if search:
        query = query.where(
            or_(Prompt.title.ilike(f"%{search}%"), Prompt.description.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.where(Prompt.category_id == category_id)
    if is_favorite is not None:
        query = query.where(Prompt.is_favorite == is_favorite)
    if tag_id:
        query = query.where(Prompt.tags.any(Tag.id == tag_id))

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    sort_col = getattr(Prompt, sort_by, Prompt.updated_at)
    order = sort_col.asc() if sort_order == "asc" else sort_col.desc()
    query = query.order_by(order).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    prompts = result.scalars().all()

    return {
        "items": [PromptListItem.model_validate(p) for p in prompts],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    req: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prompt = Prompt(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=req.title,
        content=req.content,
        description=req.description,
        variables=req.variables,
        category_id=req.category_id,
        current_version=1,
    )
    db.add(prompt)
    await db.flush()

    # Create v1 snapshot
    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        version=1,
        content=req.content,
        variables=req.variables,
        changelog="Initial version",
    )
    db.add(version)

    if req.tag_ids:
        tag_result = await db.execute(
            select(Tag).where(Tag.id.in_(req.tag_ids), Tag.user_id == current_user.id)
        )
        prompt.tags = list(tag_result.scalars().all())

    await db.flush()
    await db.refresh(prompt)
    return prompt


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: uuid.UUID,
    req: PromptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    content_changed = False
    if req.title is not None:
        prompt.title = req.title
    if req.content is not None and req.content != prompt.content:
        prompt.content = req.content
        content_changed = True
    if req.description is not None:
        prompt.description = req.description
    if req.variables is not None:
        if req.variables != (prompt.variables or []):
            prompt.variables = req.variables
            content_changed = True
    if req.category_id is not None:
        prompt.category_id = req.category_id

    if req.tag_ids is not None:
        tag_result = await db.execute(
            select(Tag).where(Tag.id.in_(req.tag_ids), Tag.user_id == current_user.id)
        )
        prompt.tags = list(tag_result.scalars().all())

    if content_changed and req.create_version:
        prompt.current_version += 1
        version = PromptVersion(
            id=uuid.uuid4(),
            prompt_id=prompt.id,
            version=prompt.current_version,
            content=prompt.content,
            variables=prompt.variables,
            changelog="Auto-save from edit",
        )
        db.add(version)

    await db.flush()
    await db.refresh(prompt)
    return prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    await db.delete(prompt)
    return None


@router.put("/{prompt_id}/favorite", response_model=ToggleFavoriteResponse)
async def toggle_favorite(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompt.is_favorite = not prompt.is_favorite
    await db.flush()
    return ToggleFavoriteResponse(is_favorite=prompt.is_favorite)


@router.put("/{prompt_id}/rating", response_model=PromptResponse)
async def set_rating(
    prompt_id: uuid.UUID,
    req: SetRatingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    prompt.rating = req.rating
    await db.flush()
    await db.refresh(prompt)
    return prompt


@router.get("/{prompt_id}/versions", response_model=List[PromptVersionResponse])
async def list_versions(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Prompt not found")

    ver_result = await db.execute(
        select(PromptVersion).where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version.desc())
    )
    return ver_result.scalars().all()


@router.post("/{prompt_id}/versions", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    prompt_id: uuid.UUID,
    req: PromptVersionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Prompt).where(Prompt.id == prompt_id, Prompt.user_id == current_user.id)
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt.current_version += 1
    version = PromptVersion(
        id=uuid.uuid4(),
        prompt_id=prompt.id,
        version=prompt.current_version,
        content=req.content,
        variables=req.variables,
        changelog=req.changelog,
    )
    db.add(version)
    await db.flush()
    await db.refresh(version)
    return version
