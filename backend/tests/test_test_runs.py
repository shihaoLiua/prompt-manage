import pytest


@pytest.mark.asyncio
async def _setup(client):
    """Register + login, return token."""
    await client.post("/api/auth/register", json={
        "username": "truser", "email": "tr@test.com", "password": "pass"
    })
    resp = await client.post("/api/auth/login", json={
        "username": "truser", "password": "pass"
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_list_test_runs(client):
    token = await _setup(client)
    # Create a prompt first
    p_resp = await client.post("/api/prompts", json={"title": "Test", "content": "test"},
                               headers={"Authorization": f"Bearer {token}"})
    pid = p_resp.json()["id"]

    # Test runs should be empty initially
    resp = await client.get(f"/api/prompts/{pid}/test-runs",
                            headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_test_run_not_found(client):
    token = await _setup(client)
    resp = await client.get(f"/api/test-runs/00000000-0000-0000-0000-000000000000",
                            headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404
