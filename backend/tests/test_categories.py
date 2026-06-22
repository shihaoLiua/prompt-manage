import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db, async_session_factory, init_db
from app.models import User, Category
from app.security import hash_password
import uuid


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with async_session_factory() as session:
        for table in reversed(Category.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest_asyncio.fixture
async def db():
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(db):
    user = User(id=uuid.uuid4(), username="catuser2", email="cat2@test.com", hashed_password=hash_password("pass"))
    db.add(user)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def token(test_user):
    from app.security import create_access_token
    return create_access_token({"sub": str(test_user.id)})


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_create_category(client, token):
    resp = await client.post("/api/categories", json={"name": "Test Cat", "sort_order": 0},
                             headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Cat"


@pytest.mark.asyncio
async def test_list_categories(client, token, db, test_user):
    c1 = Category(id=uuid.uuid4(), user_id=test_user.id, name="Cat A", sort_order=1)
    c2 = Category(id=uuid.uuid4(), user_id=test_user.id, name="Cat B", sort_order=0)
    db.add_all([c1, c2])
    await db.commit()
    resp = await client.get("/api/categories", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_category(client, token, db, test_user):
    cat = Category(id=uuid.uuid4(), user_id=test_user.id, name="To Delete")
    db.add(cat)
    await db.commit()
    resp = await client.delete(f"/api/categories/{cat.id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_unauthorized(client):
    resp = await client.get("/api/categories")
    assert resp.status_code == 401
