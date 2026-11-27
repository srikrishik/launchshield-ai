"""Import model modules here so Alembic can register their tables."""

from app.db.base import Base

__all__ = ["Base"]
