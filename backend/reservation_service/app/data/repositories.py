from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.reservation_service.app import models
from backend.reservation_service.app.schemas import ResourceCreate, UserCreate


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


class ReservationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self, user_id: int, resource_id: int, starts_at: datetime, ends_at: datetime
    ) -> models.Reservation:
        entity = models.Reservation(
            user_id=user_id,
            resource_id=resource_id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get(self, reservation_id: int) -> models.Reservation | None:
        return self.db.get(models.Reservation, reservation_id)

    def list(self) -> list[models.Reservation]:
        return list(self.db.scalars(select(models.Reservation).order_by(models.Reservation.id)))

    def has_conflict(self, resource_id: int, starts_at: datetime, ends_at: datetime) -> bool:
        query = select(models.Reservation).where(
            models.Reservation.resource_id == resource_id,
            models.Reservation.status == "confirmed",
            models.Reservation.starts_at < ends_at,
            models.Reservation.ends_at > starts_at,
        )
        return self.db.scalars(query).first() is not None

    def cancel(self, reservation: models.Reservation) -> models.Reservation:
        reservation.status = "cancelled"
        self.db.commit()
        self.db.refresh(reservation)
        return reservation
