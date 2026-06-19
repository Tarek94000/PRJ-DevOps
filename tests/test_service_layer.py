from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from backend.reservation_service.app.schemas import ReservationCreate, ResourceCreate, UserCreate
from backend.reservation_service.app.services.reservation_service import ReservationService


class FakeNotificationClient:
    def __init__(self) -> None:
        self.payloads = []

    def send(self, payload) -> None:
        self.payloads.append(payload)


def test_reservation_service_creates_reservation_and_sends_notification(db_session):
    notifier = FakeNotificationClient()
    service = ReservationService(db_session, notification_client=notifier)
    user = service.create_user(UserCreate(name="Alice", email="alice@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle B", location="Paris"))

    starts_at = datetime.now(UTC) + timedelta(days=2)
    reservation = service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
        )
    )

    assert reservation.status == "confirmed"
    assert len(notifier.payloads) == 1
    assert notifier.payloads[0].reservation_id == reservation.id


def test_reservation_service_rejects_conflicting_slot(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    user = service.create_user(UserCreate(name="Bob", email="bob@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle C", location="Lyon"))
    starts_at = datetime.now(UTC) + timedelta(days=3)

    payload = ReservationCreate(
        user_id=user.id,
        resource_id=resource.id,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )
    service.create_reservation(payload)

    with pytest.raises(HTTPException) as exc:
        service.create_reservation(payload)

    assert exc.value.status_code == 409
