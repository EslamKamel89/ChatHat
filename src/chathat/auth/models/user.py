from datetime import datetime

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from chathat.core.database.models import (
    created_at_field,
    organization_id_field,
    primary_key_field,
    updated_at_field,
)
from chathat.organizations.models.organization import Organization


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    __table_args__ = (
        UniqueConstraint("organization_id", "id"),
        CheckConstraint(
            "email <> '' AND email = lower(btrim(email))",
            name="canonical_email",
        ),
    )

    id: int | None = primary_key_field()
    organization_id: int = organization_id_field()
    email: str = Field(max_length=320, unique=True)
    is_owner: bool = Field(default=False)
    created_at: datetime | None = created_at_field()
    updated_at: datetime | None = updated_at_field()

    organization: Organization = Relationship()
