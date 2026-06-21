from datetime import UTC, datetime, timedelta

from backend.reservation_service.app.data.repositories import (
    ReservationRepository,
    ResourceRepository,
    UserRepository,
)
from backend.reservation_service.app.schemas import ReservationCreate, ResourceCreate, UserCreate


def test_repositories_create_entities_and_detect_conflict(db_session):
    users = UserRepository(db_session)
    resources = ResourceRepository(db_session)
    reservations = ReservationRepository(db_session)

    user = users.create(UserCreate(name="Tarek", email="tarek@example.com"))
    resource = resources.create(ResourceCreate(name="Salle A", location="Campus"))

    starts_at = datetime.now(UTC) + timedelta(days=1)
    ends_at = starts_at + timedelta(hours=1)
    reservation = reservations.create(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
    )

    assert reservation.id == 1
    assert users.list() == [user]
    assert resources.list() == [resource]
    assert reservations.has_conflict(resource.id, starts_at, ends_at)
    assert not reservations.has_conflict(
        resource.id,
        ends_at + timedelta(minutes=1),
        ends_at + timedelta(hours=1),
    )
