import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DatabaseConfig

from . import models

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, config: DatabaseConfig) -> None:
        self.engine = create_async_engine(
            url=config.url(),
            pool_pre_ping=True,
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.debug("Database engine and session maker initialized successfully.")

    async def initialize(self) -> Self:
        try:
            async with self.engine.begin() as connection:
                await connection.run_sync(models.Base.metadata.create_all)
            logger.debug("Database schema initialized successfully.")
        except Exception as exception:
            logger.error(f"Error initializing database schema: {exception}")
            raise
        return self

    async def close(self) -> None:
        try:
            await self.engine.dispose()
            logger.debug("Database engine closed successfully.")
        except Exception as exception:
            logger.error(f"Error closing database engine: {exception}")
            raise
