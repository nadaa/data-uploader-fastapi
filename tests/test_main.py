import pytest

@pytest.mark.asyncio
async def test_get_root(async_test_client):
    response = await async_test_client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI is running."}