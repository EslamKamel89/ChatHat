from datetime import datetime

from sqlmodel import Field, SQLModel

from chathat.core.database.models import (
    created_at_field,
    primary_key_field,
    updated_at_field,
)


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"  # type: ignore

    id: int | None = primary_key_field()
    created_at: datetime | None = created_at_field()
    updated_at: datetime | None = updated_at_field()
    name: str = Field(max_length=200)
