from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import DatabaseConfig
from . import models


class Database:
    """
    Manages database connections and operations.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Initialize the database manager.

        Arguments:
            config (DatabaseConfig): Configuration object for the database.
        """
        self.engine = create_async_engine(
            url=config.url(),
            pool_pre_ping=True,
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def initialize(self) -> "Database":
        """
        Set up the database schema.

        Returns:
            Database: The initialized database instance.
        """
        async with self.engine.begin() as connection:
            await connection.run_sync(models.Base.metadata.create_all)
        return self

    async def close(self) -> None:
        """
        Dispose of the database engine and release resources.
        """
        await self.engine.dispose()
