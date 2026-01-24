from app.db.session import engine, Base
from app.db import models

async def init_db():
    async with engine.begin() as conn:
        # In production with Alembic, we wouldn't do this drop_all/create_all directly usually,
        # but for this "fix my project" request, it ensures a clean state.
        # comment out drop_all if you want to persist data across restarts
        # await conn.run_sync(Base.metadata.drop_all) 
        await conn.run_sync(Base.metadata.create_all)
