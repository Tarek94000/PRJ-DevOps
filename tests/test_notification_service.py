from fastapi.testclient import TestClient

from backend.notification_service.app.main import app


def test_notification_service_stores_sent_notification():
    client = TestClient(app)

    response = client.post(
        "/notifications",
        json={
            "reservation_id": 10,
            "user_email": "user@example.com",
            "message": "Reservation confirmed.",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "sent"
    assert client.get("/notifications").json()
