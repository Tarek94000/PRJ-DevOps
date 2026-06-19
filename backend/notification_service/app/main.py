from fastapi import FastAPI

from backend.notification_service.app.schemas import NotificationCreate, NotificationRead
from backend.notification_service.app.services import notification_service

app = FastAPI(title="Notification Service", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/notifications", response_model=NotificationRead, status_code=201)
def create_notification(payload: NotificationCreate):
    return notification_service.send(payload)


@app.get("/notifications", response_model=list[NotificationRead])
def list_notifications():
    return notification_service.list_sent()
