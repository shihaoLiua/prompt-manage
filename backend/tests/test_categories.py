import pytest


@pytest.mark.asyncio
async def test_create_category(client):
    """Test creating a category via API."""
    await client.post("/api/auth/register", json={
        "username": "catuser", "email": "cat@test.com", "password": "pass123"
    })
    login_resp = await client.post("/api/auth/login", json={
        "username": "catuser", "password": "pass123"
    })
    token = login_resp.json()["access_token"]

    resp = await client.post("/api/categories", json={"name": "Test Cat", "sort_order": 0},
                             headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Cat"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_categories(client):
    """Test listing categories."""
    await client.post("/api/auth/register", json={
        "username": "catlist", "email": "catlist@test.com", "password": "pass"
    })
    login_resp = await client.post("/api/auth/login", json={
        "username": "catlist", "password": "pass"
    })
    token = login_resp.json()["access_token"]

    await client.post("/api/categories", json={"name": "Cat A", "sort_order": 1},
                      headers={"Authorization": f"Bearer {token}"})
    await client.post("/api/categories", json={"name": "Cat B", "sort_order": 0},
                      headers={"Authorization": f"Bearer {token}"})

    resp = await client.get("/api/categories", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_category(client):
    """Test deleting a category."""
    await client.post("/api/auth/register", json={
        "username": "catdel", "email": "catdel@test.com", "password": "pass"
    })
    login_resp = await client.post("/api/auth/login", json={
        "username": "catdel", "password": "pass"
    })
    token = login_resp.json()["access_token"]

    create_resp = await client.post("/api/categories", json={"name": "To Delete"},
                                    headers={"Authorization": f"Bearer {token}"})
    cat_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/categories/{cat_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_unauthorized(client):
    """Test that unauthenticated requests are rejected."""
    resp = await client.get("/api/categories")
    assert resp.status_code == 401
