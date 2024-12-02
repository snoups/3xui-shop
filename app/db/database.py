from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import DatabaseConfig
from . import models


class Database:
    """
    Database manager for handling database connections and operations.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Initialize the Database manager.

        Args:
            config (DatabaseConfig): The database configuration object.
        """
        self.engine = create_async_engine(
            url=config.url(),
            pool_pre_ping=True,
        )
        self.session = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init(self) -> "Database":
        """
        Initialize the database.

        Returns:
            Database: The initialized Database instance.
        """
        async with self.engine.begin() as connection:
            await connection.run_sync(models.Base.metadata.create_all)
        return self

    async def close(self) -> None:
        """
        Close the database connection.
        """
        await self.engine.dispose()
