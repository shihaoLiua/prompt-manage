from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth
# from app.routers import users, prompts, categories, tags, test_runs, batch_tests  # 后续任务实现


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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
# 注意：以下路由尚未实现，但先注册占位，后续任务会实现
# app.include_router(users.router)
# app.include_router(prompts.router)
# app.include_router(categories.router)
# app.include_router(tags.router)
# app.include_router(test_runs.router)
# app.include_router(batch_tests.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
