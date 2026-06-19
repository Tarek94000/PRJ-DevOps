from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.reservation_service.app.data.repositories import (
    ReservationRepository,
    ResourceRepository,
    UserRepository,
)
from backend.reservation_service.app.schemas import (
    NotificationPayload,
    ReservationCreate,
    ResourceCreate,
    UserCreate,
)
from backend.reservation_service.app.services.notification_client import NotificationClient


class ReservationService:
    def __init__(self, db: Session, notification_client: NotificationClient | None = None) -> None:
        self.users = UserRepository(db)
        self.resources = ResourceRepository(db)
        self.reservations = ReservationRepository(db)
        self.notification_client = notification_client or NotificationClient()

    def create_user(self, payload: UserCreate):
        try:
            return self.users.create(payload)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            ) from exc

    def create_resource(self, payload: ResourceCreate):
        return self.resources.create(payload)

    def list_resources(self):
        return self.resources.list()

    def list_reservations(self):
        return self.reservations.list()

    def create_reservation(self, payload: ReservationCreate):
        if payload.starts_at >= payload.ends_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation end must be after start.",
            )

        user = self.users.get(payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        resource = self.resources.get(payload.resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")

        if self.reservations.has_conflict(payload.resource_id, payload.starts_at, payload.ends_at):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resource is already reserved for this period.",
            )

        reservation = self.reservations.create(
            payload.user_id,
            payload.resource_id,
            payload.starts_at,
            payload.ends_at,
        )
        self.notification_client.send(
            NotificationPayload(
                reservation_id=reservation.id,
                user_email=user.email,
                message=f"Reservation confirmed for {resource.name}.",
            )
        )
        return reservation

    def cancel_reservation(self, reservation_id: int):
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found.",
            )

        cancelled = self.reservations.cancel(reservation)
        self.notification_client.send(
            NotificationPayload(
                reservation_id=cancelled.id,
                user_email=cancelled.user.email,
                message="Reservation cancelled.",
            )
        )
        return cancelled
