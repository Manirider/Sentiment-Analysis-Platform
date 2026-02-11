import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))





@pytest.mark.asyncio
async def test_health_endpoint_has_services(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]


@pytest.mark.asyncio
async def test_health_endpoint_has_stats(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "total_posts" in data["stats"]
    assert "total_analyses" in data["stats"]
    assert "recent_posts_1h" in data["stats"]


@pytest.mark.asyncio
async def test_posts_endpoint_has_pagination(client):
    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


@pytest.mark.asyncio
async def test_posts_endpoint_pagination_params(client):
    response = await client.get("/api/posts?limit=10&offset=5")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 10
    assert data["offset"] == 5


@pytest.mark.asyncio
async def test_analytics_endpoint_structure(client):
    response = await client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "positive_count" in data
    assert "negative_count" in data
    assert "neutral_count" in data
    assert "total_count" in data
    assert "percentages" in data
    assert "distribution" in data


@pytest.mark.asyncio
async def test_analytics_endpoint_percentages(client):
    response = await client.get("/api/analytics")
    data = response.json()
    assert "positive" in data["percentages"]
    assert "negative" in data["percentages"]
    assert "neutral" in data["percentages"]


@pytest.mark.asyncio
async def test_analytics_endpoint_distribution(client):
    response = await client.get("/api/analytics")
    data = response.json()
    assert isinstance(data["distribution"], list)
    assert len(data["distribution"]) == 3
    for item in data["distribution"]:
        assert "label" in item
        assert "count" in item
        assert "percentage" in item


@pytest.mark.asyncio
async def test_analytics_endpoint_hours_param(client):
    response = await client.get("/api/analytics?hours=48")
    assert response.status_code == 200
    data = response.json()
    assert data["timeframe_hours"] == 48


@pytest.mark.asyncio
async def test_health_endpoint_status(client):
    response = await client.get("/api/health")
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded", "unhealthy"]
    assert "timestamp" in data
