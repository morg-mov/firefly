import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

async def initialize_database(sqlalc_uri: str, filepath: str, model: DeclarativeBase):
    if not os.path.isdir(filepath):
        os.makedirs(filepath)

    engine = create_async_engine(sqlalc_uri)
    
    async with engine.begin() as conn:
        await conn.run_sync(model.metadata.create_all)

    await engine.dispose()