import os
from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer,
    Enum as PgEnum,
    DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from procycling_scraper.scraping.domain.entities.race import RaceType

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL).execution_options(
    isolation_level="AUTOCOMMIT"
)

metadata = MetaData()

riders_table = Table(
    'riders', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True,
           server_default=func.gen_random_uuid()),
    Column('pcs_id', String, unique=True, nullable=False, index=True),
    Column('name', String, nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
    Column('updated_at', DateTime, nullable=False,
           server_default=func.now(), onupdate=func.now())
)

races_table = Table(
    'races', metadata,
    Column('id', UUID(as_uuid=True), primary_key=True,
           server_default=func.gen_random_uuid()),
    Column('pcs_id', String, unique=True, nullable=False, index=True),
    Column('name', String, nullable=False),
    Column('year', Integer, nullable=False),
    Column('type', PgEnum(RaceType, name="race_type_enum"), nullable=False),
    Column('created_at', DateTime, nullable=False, server_default=func.now()),
    Column('updated_at', DateTime, nullable=False,
           server_default=func.now(), onupdate=func.now())
)
