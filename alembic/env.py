import os
from logging.config import fileConfig
from typing import Any, Dict, Optional, cast

import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool

from alembic import context  # type: ignore[attr-defined]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Load DATABASE_URL from env and set sqlalchemy.url dynamically
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Import metadata from the project
# We avoid importing full app; only bring the metadata to autogenerate
from procycling_scraper.scraping.infrastructure.database.schema import (  # noqa: E402
    metadata,
)

target_metadata = metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg_section: Dict[str, Any] = cast(
        Dict[str, Any], config.get_section(config.config_ini_section) or {}
    )
    connectable = engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            # Ensure pgcrypto extension exists for gen_random_uuid
            connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
            context.run_migrations()


def include_object(
    object: Any,
    name: Optional[str],
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    # Include enums and everything else by default
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
