from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr


class UserRead(UserCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserSummary(UserRead):
    reservations_count: int = 0


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)
    capacity: int = Field(default=1, ge=1)
    resource_type: str = Field(default="room", min_length=2, max_length=60)
    description: str = Field(default="", max_length=1000)
    equipment: list[str] = Field(default_factory=list)
    is_active: bool = True


class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    location: str | None = Field(default=None, min_length=2, max_length=120)
    capacity: int | None = Field(default=None, ge=1)
    resource_type: str | None = Field(default=None, min_length=2, max_length=60)
    description: str | None = Field(default=None, max_length=1000)
    equipment: list[str] | None = None
    is_active: bool | None = None


class ResourceRead(ResourceCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    user_id: int
    resource_id: int
    title: str = Field(default="Reservation", min_length=2, max_length=160)
    purpose: str = Field(default="", max_length=1000)
    attendees_count: int = Field(default=1, ge=1)
    starts_at: datetime
    ends_at: datetime


class ReservationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    purpose: str | None = Field(default=None, max_length=1000)
    attendees_count: int | None = Field(default=None, ge=1)
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class ReservationRead(ReservationCreate):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationPayload(BaseModel):
    reservation_id: int
    user_email: EmailStr
    message: str
    event_type: str


class DashboardRead(BaseModel):
    total_resources: int
    active_resources: int
    inactive_resources: int
    active_reservations: int
    cancelled_reservations: int
    upcoming_reservations: int
