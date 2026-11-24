from datetime import datetime

from sqlmodel import DateTime, Field, func


def primary_key_field() -> int | None:
    return Field(default=None, primary_key=True)


def created_at_field() -> datetime:
    return Field(
        default=None,
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )


def updated_at_field() -> datetime:
    return Field(
        default=None,
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


def organization_id_field() -> int:
    return Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True,
    )
