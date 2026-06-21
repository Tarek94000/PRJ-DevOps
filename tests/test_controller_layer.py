from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from backend.reservation_service.app.controllers import routes
from backend.reservation_service.app.main import app
from backend.reservation_service.app.services.reservation_service import ReservationService


class FakeNotificationClient:
    def send(self, payload) -> None:
        return None


def test_reservation_api_happy_path(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    app.dependency_overrides[routes.get_service] = lambda: service
    client = TestClient(app)

    user_response = client.post(
        "/users",
        json={"name": "Chloe", "email": "chloe@example.com"},
    )
    resource_response = client.post(
        "/resources",
        json={"name": "Salle D", "location": "Bordeaux"},
    )
    starts_at = datetime.now(UTC) + timedelta(days=4)
    reservation_response = client.post(
        "/reservations",
        json={
            "user_id": user_response.json()["id"],
            "resource_id": resource_response.json()["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
        },
    )

    app.dependency_overrides.clear()

    assert user_response.status_code == 201
    assert resource_response.status_code == 201
    assert reservation_response.status_code == 201
    assert reservation_response.json()["status"] == "confirmed"


def test_reservation_api_validates_end_after_start(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    app.dependency_overrides[routes.get_service] = lambda: service
    client = TestClient(app)
    user = client.post("/users", json={"name": "Dan", "email": "dan@example.com"}).json()
    resource = client.post("/resources", json={"name": "Salle E", "location": "Nice"}).json()
    starts_at = datetime.now(UTC) + timedelta(days=5)

    response = client.post(
        "/reservations",
        json={
            "user_id": user["id"],
            "resource_id": resource["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": starts_at.isoformat(),
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 400


def test_reservation_api_exposes_dashboard_and_updates(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    app.dependency_overrides[routes.get_service] = lambda: service
    client = TestClient(app)

    user = client.post("/users", json={"name": "Lea", "email": "lea@example.com"}).json()
    resource = client.post(
        "/resources",
        json={
            "name": "Salle F",
            "location": "Marseille",
            "capacity": 8,
            "resource_type": "meeting-room",
            "description": "Grande salle",
            "equipment": ["wifi", "screen"],
        },
    ).json()
    patched_resource = client.patch(
        f"/resources/{resource['id']}",
        json={"capacity": 10, "description": "Salle equipee"},
    )
    starts_at = datetime.now(UTC) + timedelta(days=6)
    reservation = client.post(
        "/reservations",
        json={
            "user_id": user["id"],
            "resource_id": resource["id"],
            "title": "Atelier CI",
            "purpose": "Preparation demo",
            "attendees_count": 5,
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
        },
    ).json()
    updated_reservation = client.patch(
        f"/reservations/{reservation['id']}",
        json={"title": "Atelier CI/CD", "attendees_count": 6},
    )
    fetched_user = client.get(f"/users/{user['id']}")
    dashboard = client.get("/dashboard")
    cancelled = client.post(f"/reservations/{reservation['id']}/cancel")
    deactivated = client.delete(f"/resources/{resource['id']}")

    app.dependency_overrides.clear()

    assert fetched_user.status_code == 200
    assert patched_resource.json()["capacity"] == 10
    assert updated_reservation.json()["title"] == "Atelier CI/CD"
    assert dashboard.status_code == 200
    assert dashboard.json()["total_resources"] == 1
    assert cancelled.json()["status"] == "cancelled"
    assert deactivated.json()["is_active"] is False
