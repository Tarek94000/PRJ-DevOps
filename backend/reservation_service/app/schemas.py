from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class UserRead(UserCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)


class ResourceRead(ResourceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    user_id: int
    resource_id: int
    starts_at: datetime
    ends_at: datetime


class ReservationRead(ReservationCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class NotificationPayload(BaseModel):
    reservation_id: int
    user_email: EmailStr
    message: str
