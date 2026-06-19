import httpx

from backend.reservation_service.app.config import settings
from backend.reservation_service.app.schemas import NotificationPayload


class NotificationClient:
    def __init__(self, base_url: str = settings.notification_service_url) -> None:
        self.base_url = base_url.rstrip("/")

    def send(self, payload: NotificationPayload) -> None:
        with httpx.Client(timeout=3.0) as client:
            response = client.post(f"{self.base_url}/notifications", json=payload.model_dump())
            response.raise_for_status()
