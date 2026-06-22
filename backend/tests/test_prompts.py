import pytest


@pytest.mark.asyncio
async def _auth_and_token(client):
    """Helper to register+login and return token."""
    await client.post("/api/auth/register", json={
        "username": "pruser", "email": "pr@test.com", "password": "pass"
    })
    resp = await client.post("/api/auth/login", json={
        "username": "pruser", "password": "pass"
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_prompt(client):
    token = await _auth_and_token(client)
    resp = await client.post("/api/prompts", json={
        "title": "Test Prompt",
        "content": "Hello {{name}}",
        "description": "A test",
        "variables": [{"name": "name", "label": "Name", "default": "World", "type": "text"}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Prompt"
    assert data["current_version"] == 1


@pytest.mark.asyncio
async def test_list_prompts(client):
    token = await _auth_and_token(client)
    # Create one prompt
    await client.post("/api/prompts", json={"title": "My Prompt", "content": "test"},
                      headers={"Authorization": f"Bearer {token}"})
    resp = await client.get("/api/prompts", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


@pytest.mark.asyncio
async def test_get_prompt(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Detail", "content": "detail test"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.get(f"/api/prompts/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "Detail"


@pytest.mark.asyncio
async def test_update_prompt(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Old", "content": "old content"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.put(f"/api/prompts/{pid}", json={"title": "New", "content": "new content"},
                            headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


@pytest.mark.asyncio
async def test_delete_prompt(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Del", "content": "bye"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.delete(f"/api/prompts/{pid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_toggle_favorite(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Fav", "content": "test"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.put(f"/api/prompts/{pid}/favorite", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True


@pytest.mark.asyncio
async def test_set_rating(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Rate", "content": "test"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.put(f"/api/prompts/{pid}/rating", json={"rating": 4},
                            headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["rating"] == 4


@pytest.mark.asyncio
async def test_create_version(client):
    token = await _auth_and_token(client)
    create_resp = await client.post("/api/prompts", json={"title": "Ver", "content": "v1"},
                                    headers={"Authorization": f"Bearer {token}"})
    pid = create_resp.json()["id"]
    resp = await client.post(f"/api/prompts/{pid}/versions", json={
        "content": "v2 content",
        "changelog": "Updated",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.json()["version"] == 2  # initial v1 + this = v2
