"""SQLAlchemy declarative base."""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase

# BIGINT on PostgreSQL (for very large tables) but INTEGER on SQLite,
# which only auto-increments `INTEGER PRIMARY KEY`.
BigIntPK = BigInteger().with_variant(Integer, "sqlite")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class IdMixin:
    id = Column(String(32), primary_key=True)
