import asyncio
from app.database.database import AsyncSessionLocal
from app.models.client import Client
from sqlalchemy import select
async def main():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Client).limit(1))
        c = res.scalar_one_or_none()
        if c:
            print(repr(c.plan_start_date))
asyncio.run(main())
