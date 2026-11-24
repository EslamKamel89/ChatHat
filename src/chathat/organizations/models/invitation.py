from datetime import datetime

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import DateTime, Field, Relationship, SQLModel

from chathat.auth.models.user import User
from chathat.core.database.models import (
    created_at_field,
    organization_id_field,
    primary_key_field,
    updated_at_field,
)
from chathat.organizations.models.organization import Organization


class Invitation(SQLModel, table=True):
    __tablename__ = "invitations"  # type: ignore

    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "invited_by_user_id"],
            ["users.organization_id", "users.id"],
            name="fk_invitations_organization_id_invited_by_user_id",
        ),
    )

    id: int | None = primary_key_field()
    organization_id: int = organization_id_field()
    invited_by_user_id: int = Field(nullable=False)
    token_digest: str = Field(max_length=64, unique=True)
    email: str = Field(max_length=320)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    accepted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
        nullable=True,
    )
    created_at: datetime | None = created_at_field()
    updated_at: datetime | None = updated_at_field()

    organization: Organization = Relationship()
    invited_by_user: User = Relationship(sa_relationship_kwargs={"viewonly": True})
