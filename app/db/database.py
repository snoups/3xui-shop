import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DatabaseConfig

from . import models

logger = logging.getLogger(__name__)


class Database:
    """
    Manages database connections and operations.

    This class is responsible for creating and managing the database connection engine,
    initializing the database schema, and handling asynchronous sessions for interacting
    with the database.

    Attributes:
        engine: The SQLAlchemy async engine used for database connections.
        session: The session maker for creating async database sessions.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """
        Initialize the database manager.

        Sets up the asynchronous SQLAlchemy engine and session maker.

        Arguments:
            config (DatabaseConfig): Configuration object for the database, including URL.
        """
        logger.debug("Initializing database engine and session maker.")
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
        """
        Set up the database schema.

        Creates the necessary database tables if they don't exist already.

        Returns:
            Database: The initialized database instance with a created schema.
        """
        logger.debug("Starting database schema initialization.")
        try:
            async with self.engine.begin() as connection:
                await connection.run_sync(models.Base.metadata.create_all)
            logger.debug("Database schema initialized successfully.")
        except Exception as exception:
            logger.error(f"Error initializing database schema: {exception}")
            raise
        return self

    async def close(self) -> None:
        """
        Dispose of the database engine and release resources.

        Disposes the engine, releasing any associated resources,
        such as database connections, when no longer needed.
        """
        logger.info("Closing database engine and releasing resources.")
        try:
            await self.engine.dispose()
            logger.info("Database engine closed successfully.")
        except Exception as exception:
            logger.error(f"Error closing database engine: {exception}")
            raise
