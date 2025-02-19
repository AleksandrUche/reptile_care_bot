from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import asyncio

from config_data.config import DB_USER, DB_NAME, DB_PASS, DB_HOST, DB_PORT


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, 'DB_USER', DB_USER)
config.set_section_option(section, 'DB_NAME', DB_NAME)
config.set_section_option(section, 'DB_PASS', DB_PASS)
config.set_section_option(section, 'DB_HOST', DB_HOST)
config.set_section_option(section, 'DB_PORT', DB_PORT)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

from database.models.user_models import Base
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(connection=connection, target_metadata=target_metadata)

#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()

async def run_async_migrations():
    """Запуск асинхронных миграций."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=True,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(lambda sync_conn: context.configure(
            connection=sync_conn,
            target_metadata=target_metadata,
            compare_type=True,
        ))

        async with connection.begin():
            await connection.run_sync(lambda sync_conn: context.run_migrations())

def run_migrations_online():
    """Запуск миграций в онлайн-режиме."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
