from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from database.models import Base
from utils.config import config

config_alembic = context.config
config_alembic.set_main_option("sqlalchemy.url", config.db.url)

if config_alembic.config_file_name is not None:
    fileConfig(config_alembic.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=config_alembic.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = AsyncEngine(
        engine_from_config(
            config_alembic.get_section(config_alembic.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            context.configure, connection=connection, target_metadata=target_metadata
        )
        async with context.begin_transaction():
            await connection.run_sync(context.run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    context.run_sync(run_migrations_online)
