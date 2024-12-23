from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import DatabaseConfig
from . import models


class Database:
    """
    Manages database connections and operations.

    This class is responsible for creating and managing the database connection engine,
    initializing the database schema, and handling asynchronous sessions for interacting
    with the database.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Initialize the database manager.

        This method sets up the asynchronous SQLAlchemy engine and session maker.

        Arguments:
            config (DatabaseConfig): Configuration object for the database, including URL.
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

        This method creates the necessary database tables if they don't exist already,
        by running the schema creation commands on the database engine.

        Returns:
            Database: The initialized database instance with a created schema.
        """
        async with self.engine.begin() as connection:
            await connection.run_sync(models.Base.metadata.create_all)
        return self

    async def close(self) -> None:
        """
        Dispose of the database engine and release resources.

        This method disposes of the engine, releasing any associated resources,
        such as database connections, when no longer needed.
        """
        await self.engine.dispose()
