import pytest


@pytest.mark.asyncio
async def _setup(client):
    await client.post("/api/auth/register", json={
        "username": "batuser", "email": "bat@test.com", "password": "pass"
    })
    resp = await client.post("/api/auth/login", json={
        "username": "batuser", "password": "pass"
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_batch_test(client):
    token = await _setup(client)
    p_resp = await client.post("/api/prompts", json={"title": "Batch", "content": "test"},
                               headers={"Authorization": f"Bearer {token}"})
    pid = p_resp.json()["id"]

    resp = await client.post(f"/api/prompts/{pid}/batch-test", json={
        "name": "My Batch",
        "configs": [
            {"api_config_id": "00000000-0000-0000-0000-000000000001", "model": "gpt-4", "label": "GPT-4"},
            {"api_config_id": "00000000-0000-0000-0000-000000000002", "model": "gpt-3.5", "label": "GPT-3.5"},
        ],
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Batch"
    assert data["total_count"] == 2
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_batch_tests(client):
    token = await _setup(client)
    p_resp = await client.post("/api/prompts", json={"title": "B", "content": "c"},
                               headers={"Authorization": f"Bearer {token}"})
    pid = p_resp.json()["id"]

    await client.post(f"/api/prompts/{pid}/batch-test", json={
        "name": "Batch 1", "configs": [],
    }, headers={"Authorization": f"Bearer {token}"})

    resp = await client.get("/api/batch-tests", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_batch(client):
    token = await _setup(client)
    p_resp = await client.post("/api/prompts", json={"title": "B2", "content": "c"},
                               headers={"Authorization": f"Bearer {token}"})
    pid = p_resp.json()["id"]

    create_resp = await client.post(f"/api/prompts/{pid}/batch-test", json={
        "name": "Del Me", "configs": [],
    }, headers={"Authorization": f"Bearer {token}"})
    bid = create_resp.json()["id"]

    resp = await client.delete(f"/api/batch-tests/{bid}",
                               headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204
