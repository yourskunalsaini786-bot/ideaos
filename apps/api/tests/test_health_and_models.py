"""Basic test suite verifying backend health and model loading."""
import asyncio
from httpx import ASGITransport, AsyncClient
from ideaos.main import app
from ideaos.core.database import init_db, close_db, get_db_context
from ideaos.models import User


def test_health_endpoints():
    async def run():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "healthy"
            assert data["service"] == "ideaos-api"

            resp_root = await client.get("/")
            assert resp_root.status_code == 200
            assert resp_root.json()["status"] == "running"

    asyncio.run(run())


def test_database_initialization():
    async def run():
        await init_db()
        async with get_db_context() as session:
            from sqlalchemy import select
            res = await session.execute(select(User))
            users = res.scalars().all()
            assert isinstance(users, list)
        await close_db()

    asyncio.run(run())
