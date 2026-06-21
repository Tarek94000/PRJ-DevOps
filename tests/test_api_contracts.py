from fastapi.testclient import TestClient

from backend.notification_service.app.main import app as notification_app
from backend.reservation_service.app.controllers import routes
from backend.reservation_service.app.main import app as reservation_app
from backend.reservation_service.app.services.reservation_service import ReservationService


class FakeNotificationClient:
    def send(self, payload) -> None:
        return None


def test_reservation_service_health_and_openapi_contract(db_session):
    service = ReservationService(db_session, notification_client=FakeNotificationClient())
    reservation_app.dependency_overrides[routes.get_service] = lambda: service
    client = TestClient(reservation_app)

    health = client.get("/health")
    openapi = client.get("/openapi.json")

    reservation_app.dependency_overrides.clear()

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Reservation Service"
    assert "/reservations" in openapi.json()["paths"]
    assert "/dashboard" in openapi.json()["paths"]


def test_notification_service_health_and_openapi_contract():
    client = TestClient(notification_app)

    health = client.get("/health")
    openapi = client.get("/openapi.json")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "Notification Service"
    assert "/notifications" in openapi.json()["paths"]
