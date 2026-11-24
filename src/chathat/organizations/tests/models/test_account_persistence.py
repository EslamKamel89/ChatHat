import asyncio
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from chathat.auth.models.user import User
from chathat.core.tests.database.support import (
    database_resources,
    disposable_database,
    migrate,
)
from chathat.organizations.models.invitation import Invitation
from chathat.organizations.models.organization import Organization


OWNER_EMAIL = "owner@north.example"
TOKEN_DIGEST = "a" * 64


@pytest.fixture
def migrated_url() -> Iterator[URL]:
    with disposable_database() as url:
        migrate(url, "head")
        yield url


async def seed_tenants(session: AsyncSession) -> tuple[int, int, int]:
    north = Organization(name="North Studio")
    south = Organization(name="South Studio")
    session.add_all([north, south])
    await session.flush()
    assert north.id is not None
    assert south.id is not None

    owner = User(organization_id=north.id, email=OWNER_EMAIL, is_owner=True)
    session.add(owner)
    await session.flush()
    assert owner.id is not None
    return north.id, south.id, owner.id


def test_owner_can_persist_invitation_for_own_organization(
    migrated_url: URL,
) -> None:
    async def scenario() -> None:
        async with database_resources(migrated_url) as database:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            async with database.sessions.begin() as session:
                north_id, _, owner_id = await seed_tenants(session)
                invitation = Invitation(
                    organization_id=north_id,
                    invited_by_user_id=owner_id,
                    email="member@north.example",
                    token_digest=TOKEN_DIGEST,
                    expires_at=expires_at,
                )
                session.add(invitation)
                await session.flush()
                assert invitation.id is not None
                invitation_id = invitation.id

            async with database.sessions() as session:
                saved = await session.get(Invitation, invitation_id)
                assert saved is not None
                assert saved.organization_id == north_id
                assert saved.invited_by_user_id == owner_id
                assert saved.email == "member@north.example"
                assert saved.expires_at == expires_at
                assert saved.accepted_at is None

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("tenant", "email", "sqlstate"),
    [
        pytest.param("missing", "member@north.example", "23502", id="required-org"),
        pytest.param("unknown", "member@north.example", "23503", id="unknown-org"),
        pytest.param("south", OWNER_EMAIL, "23505", id="duplicate-across-orgs"),
        pytest.param("north", "Owner@north.example", "23514", id="uppercase-email"),
        pytest.param("north", " member@north.example ", "23514", id="padded-email"),
        pytest.param("north", "", "23514", id="empty-email"),
    ],
)
def test_user_membership_and_email_constraints(
    migrated_url: URL,
    tenant: str,
    email: str,
    sqlstate: str,
) -> None:
    async def scenario() -> None:
        async with database_resources(migrated_url) as database:
            async with database.sessions.begin() as session:
                north_id, south_id, owner_id = await seed_tenants(session)

            organization_ids = {
                "missing": None,
                "unknown": -1,
                "north": north_id,
                "south": south_id,
            }
            with pytest.raises(IntegrityError) as caught:
                async with database.sessions.begin() as session:
                    session.add(
                        User(organization_id=organization_ids[tenant], email=email)
                    )
                    await session.flush()

            assert caught.value.orig.sqlstate == sqlstate

            async with database.sessions() as session:
                owner = await session.get(User, owner_id)
                assert owner is not None
                assert owner.organization_id == north_id

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("scenario_name", "sqlstate"),
    [
        pytest.param("cross-tenant", "23503", id="cross-tenant-issuer"),
        pytest.param("unknown-issuer", "23503", id="unknown-issuer"),
        pytest.param("duplicate-digest", "23505", id="duplicate-token-digest"),
    ],
)
def test_invitation_issuer_and_token_constraints(
    migrated_url: URL,
    scenario_name: str,
    sqlstate: str,
) -> None:
    async def scenario() -> None:
        async with database_resources(migrated_url) as database:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

            async with database.sessions.begin() as session:
                north_id, south_id, owner_id = await seed_tenants(session)
                session.add(
                    Invitation(
                        organization_id=north_id,
                        invited_by_user_id=owner_id,
                        email="member@north.example",
                        token_digest=TOKEN_DIGEST,
                        expires_at=expires_at,
                    )
                )

            organization_id = south_id if scenario_name == "cross-tenant" else north_id
            issuer_id = -1 if scenario_name == "unknown-issuer" else owner_id
            digest = TOKEN_DIGEST if scenario_name == "duplicate-digest" else "b" * 64

            with pytest.raises(IntegrityError) as caught:
                async with database.sessions.begin() as session:
                    session.add(
                        Invitation(
                            organization_id=organization_id,
                            invited_by_user_id=issuer_id,
                            email="another@example.test",
                            token_digest=digest,
                            expires_at=expires_at,
                        )
                    )
                    await session.flush()

            assert caught.value.orig.sqlstate == sqlstate

    asyncio.run(scenario())
