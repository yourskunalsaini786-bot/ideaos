"""Database models - Base and Mixins."""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Index,
    UniqueConstraint,
    event,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import declarative_base, declared_attr, relationship
from sqlalchemy.ext.compiler import compiles

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

from sqlalchemy.types import TypeDecorator
from sqlalchemy import JSON

class CompatibleArray(TypeDecorator):
    """PostgreSQL ARRAY on Postgres, JSON with UUID serialization on SQLite."""
    impl = ARRAY
    cache_ok = True

    def __init__(self, item_type, *args, **kwargs):
        super().__init__(item_type, *args, **kwargs)
        self.item_type = item_type

    def load_dialect_impl(self, dialect):
        if dialect.name == "sqlite":
            return dialect.type_descriptor(JSON())
        return dialect.type_descriptor(ARRAY(self.item_type))

    def process_bind_param(self, value, dialect):
        if dialect.name == "sqlite" and value is not None:
            return [str(v) if hasattr(v, "hex") else v for v in value]
        return value

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


class WorkspaceMixin:
    """Mixin for workspace-scoped models with RLS."""
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class UUIDPrimaryKey:
    """Mixin for UUID primary key."""
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)