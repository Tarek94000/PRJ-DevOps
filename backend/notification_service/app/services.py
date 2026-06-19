from backend.notification_service.app.schemas import NotificationCreate, NotificationRead


class NotificationService:
    def __init__(self) -> None:
        self._sent: list[NotificationRead] = []

    def send(self, payload: NotificationCreate) -> NotificationRead:
        notification = NotificationRead(
            id=len(self._sent) + 1,
            status="sent",
            **payload.model_dump(),
        )
        self._sent.append(notification)
        return notification

    def list_sent(self) -> list[NotificationRead]:
        return self._sent


notification_service = NotificationService()
