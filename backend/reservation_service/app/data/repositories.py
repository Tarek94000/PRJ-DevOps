from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.reservation_service.app import models
from backend.reservation_service.app.schemas import (
    ReservationCreate,
    ResourceCreate,
    ResourceUpdate,
    UserCreate,
)


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: UserCreate) -> models.User:
        entity = models.User(**user.model_dump())
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, user_id: int) -> models.User | None:
        return self.db.get(models.User, user_id)

    def list(self) -> list[models.User]:
        return list(self.db.scalars(select(models.User).order_by(models.User.id)))


class ResourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, resource: ResourceCreate) -> models.Resource:
        entity = models.Resource(**resource.model_dump())
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, resource_id: int) -> models.Resource | None:
        return self.db.get(models.Resource, resource_id)

    def list(self) -> list[models.Resource]:
        return list(self.db.scalars(select(models.Resource).order_by(models.Resource.id)))

    def update(self, resource: models.Resource, payload: ResourceUpdate) -> models.Resource:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(resource, field, value)
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def deactivate(self, resource: models.Resource) -> models.Resource:
        resource.is_active = False
        self.db.commit()
        self.db.refresh(resource)
        return resource


class ReservationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ReservationCreate) -> models.Reservation:
        entity = models.Reservation(
            **payload.model_dump(),
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, reservation_id: int) -> models.Reservation | None:
        return self.db.get(models.Reservation, reservation_id)

    def list(self) -> list[models.Reservation]:
        return list(self.db.scalars(select(models.Reservation).order_by(models.Reservation.id)))

    def has_conflict(
        self,
        resource_id: int,
        starts_at: datetime,
        ends_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> bool:
        query = select(models.Reservation).where(
            models.Reservation.resource_id == resource_id,
            models.Reservation.status == "confirmed",
            models.Reservation.starts_at < ends_at,
            models.Reservation.ends_at > starts_at,
        )
        if exclude_reservation_id is not None:
            query = query.where(models.Reservation.id != exclude_reservation_id)
        return self.db.scalars(query).first() is not None

    def update(
        self,
        reservation: models.Reservation,
        starts_at: datetime,
        ends_at: datetime,
        title: str,
        purpose: str,
        attendees_count: int,
    ) -> models.Reservation:
        reservation.starts_at = starts_at
        reservation.ends_at = ends_at
        reservation.title = title
        reservation.purpose = purpose
        reservation.attendees_count = attendees_count
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def cancel(self, reservation: models.Reservation) -> models.Reservation:
        reservation.status = "cancelled"
        self.db.commit()
        self.db.refresh(reservation)
        return reservation
