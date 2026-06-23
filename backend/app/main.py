from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import settings
from app.database import engine, Base, async_session_factory
from app.models import User
from app.security import hash_password
from app.routers import auth, users, categories, tags, prompts, test_runs, batch_tests


async def seed_admin():
    """Create default admin user if not exists."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        if not result.scalar_one_or_none():
            import uuid
            admin = User(
                id=uuid.uuid4(),
                username="admin",
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
                is_admin=True,
                is_active=True,
            )
            session.add(admin)
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_admin()
    yield
    await engine.dispose()


app = FastAPI(
    title="Prompt Manager API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(prompts.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(test_runs.router)
app.include_router(batch_tests.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
