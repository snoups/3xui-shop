import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import load_config
from app.db.models import Base

database = load_config().database

config = context.config
config.set_main_option("sqlalchemy.url", database.url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Configures the context with just a URL (without an engine).
    By skipping engine creation, a DBAPI is not required. The migration
    script is executed by emitting the SQL commands to the script output.

    This is useful when migrations need to be run outside of a database
    engine context (for example, when generating SQL files for review).
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run migrations in the 'online' mode using an established database connection.

    This function is responsible for applying migrations to the database
    using the provided connection object. It is called by the asynchronous
    migration function when the database engine is available.

    Arguments:
        connection (Connection): SQLAlchemy connection object to interact with the database.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode asynchronously.

    Creates an asynchronous engine and establishes a connection to the database.
    The migrations are then applied asynchronously, enabling non-blocking
    operations. After the migrations are applied, the connection is disposed of.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (asynchronously).

    This function is the entry point for running migrations when in 'online' mode.
    It triggers the asynchronous migration function, ensuring that migrations
    are applied using an asynchronous connection.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
