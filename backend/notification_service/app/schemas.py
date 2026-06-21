from pydantic import BaseModel, EmailStr


class NotificationCreate(BaseModel):
    reservation_id: int
    user_email: EmailStr
    message: str
    event_type: str


class NotificationRead(NotificationCreate):
    id: int
    status: str
