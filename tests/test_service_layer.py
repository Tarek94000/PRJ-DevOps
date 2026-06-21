from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from backend.reservation_service.app.schemas import (
    ReservationCreate,
    ReservationUpdate,
    ResourceCreate,
    UserCreate,
)
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
    resource = service.create_resource(ResourceCreate(name="Salle B", location="Paris", capacity=4))

    starts_at = datetime.now(UTC) + timedelta(days=2)
    reservation = service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            title="Daily sync",
            purpose="Projet DevOps",
            attendees_count=3,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
        )
    )

    assert reservation.status == "confirmed"
    assert len(notifier.payloads) == 1
    assert notifier.payloads[0].reservation_id == reservation.id
    assert notifier.payloads[0].event_type == "reservation_created"


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


def test_reservation_service_rejects_capacity_overflow(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    user = service.create_user(UserCreate(name="Eve", email="eve@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle F", location="Paris", capacity=2))
    starts_at = datetime.now(UTC) + timedelta(days=6)

    with pytest.raises(HTTPException) as exc:
        service.create_reservation(
            ReservationCreate(
                user_id=user.id,
                resource_id=resource.id,
                attendees_count=3,
                starts_at=starts_at,
                ends_at=starts_at + timedelta(hours=1),
            )
        )

    assert exc.value.status_code == 400
    assert "capacity" in exc.value.detail


def test_reservation_service_rejects_inactive_resource(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    user = service.create_user(UserCreate(name="Farah", email="farah@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle G", location="Lille"))
    service.deactivate_resource(resource.id)
    starts_at = datetime.now(UTC) + timedelta(days=7)

    with pytest.raises(HTTPException) as exc:
        service.create_reservation(
            ReservationCreate(
                user_id=user.id,
                resource_id=resource.id,
                starts_at=starts_at,
                ends_at=starts_at + timedelta(hours=1),
            )
        )

    assert exc.value.status_code == 400
    assert "inactive" in exc.value.detail


def test_reservation_service_rejects_conflict_on_update(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    user = service.create_user(UserCreate(name="Gina", email="gina@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle H", location="Rennes"))
    first_start = datetime.now(UTC) + timedelta(days=8)
    second_start = first_start + timedelta(hours=2)

    service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=first_start,
            ends_at=first_start + timedelta(hours=1),
        )
    )
    second = service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=second_start,
            ends_at=second_start + timedelta(hours=1),
        )
    )

    with pytest.raises(HTTPException) as exc:
        service.update_reservation(
            second.id,
            ReservationUpdate(
                starts_at=first_start + timedelta(minutes=15),
                ends_at=first_start + timedelta(minutes=45),
            ),
        )

    assert exc.value.status_code == 409


def test_reservation_service_rejects_double_cancel(db_session):
    notifier = FakeNotificationClient()
    service = ReservationService(db_session, notification_client=notifier)
    user = service.create_user(UserCreate(name="Hugo", email="hugo@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle I", location="Nantes"))
    starts_at = datetime.now(UTC) + timedelta(days=9)
    reservation = service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
        )
    )

    service.cancel_reservation(reservation.id)

    with pytest.raises(HTTPException) as exc:
        service.cancel_reservation(reservation.id)

    assert exc.value.status_code == 400
    assert notifier.payloads[-1].event_type == "reservation_cancelled"


def test_reservation_service_dashboard_counts(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    user = service.create_user(UserCreate(name="Iris", email="iris@example.com"))
    resource = service.create_resource(ResourceCreate(name="Salle J", location="Dijon"))
    inactive = service.create_resource(ResourceCreate(name="Salle K", location="Dijon"))
    service.deactivate_resource(inactive.id)
    starts_at = datetime.now(UTC) + timedelta(days=10)
    reservation = service.create_reservation(
        ReservationCreate(
            user_id=user.id,
            resource_id=resource.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
        )
    )
    service.cancel_reservation(reservation.id)

    dashboard = service.dashboard()

    assert dashboard["total_resources"] == 2
    assert dashboard["active_resources"] == 1
    assert dashboard["inactive_resources"] == 1
    assert dashboard["cancelled_reservations"] == 1
