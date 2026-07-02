"""Declarative base for all ORM models.

Import model modules here (or ensure they are imported before metadata is used)
so Alembic autogeneration and create_all can see them.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
