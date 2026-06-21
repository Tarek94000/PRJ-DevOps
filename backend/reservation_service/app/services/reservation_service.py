from datetime import UTC, datetime

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
    ReservationUpdate,
    ResourceCreate,
    ResourceUpdate,
    UserCreate,
)
from backend.reservation_service.app.services.notification_client import NotificationClient


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


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

    def list_users(self):
        return self.users.list()

    def get_user(self, user_id: int):
        user = self.users.get(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    def create_resource(self, payload: ResourceCreate):
        return self.resources.create(payload)

    def get_resource(self, resource_id: int):
        resource = self.resources.get(resource_id)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found.")
        return resource

    def list_resources(self):
        return self.resources.list()

    def update_resource(self, resource_id: int, payload: ResourceUpdate):
        resource = self.get_resource(resource_id)
        return self.resources.update(resource, payload)

    def deactivate_resource(self, resource_id: int):
        resource = self.get_resource(resource_id)
        return self.resources.deactivate(resource)

    def get_reservation(self, reservation_id: int):
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found.",
            )
        return reservation

    def list_reservations(self):
        return self.reservations.list()

    def dashboard(self):
        resources = self.resources.list()
        reservations = self.reservations.list()
        now = datetime.now(UTC)
        return {
            "total_resources": len(resources),
            "active_resources": sum(1 for resource in resources if resource.is_active),
            "inactive_resources": sum(1 for resource in resources if not resource.is_active),
            "active_reservations": sum(
                1 for reservation in reservations if reservation.status == "confirmed"
            ),
            "cancelled_reservations": sum(
                1 for reservation in reservations if reservation.status == "cancelled"
            ),
            "upcoming_reservations": sum(
                1
                for reservation in reservations
                if reservation.status == "confirmed" and as_utc(reservation.starts_at) > now
            ),
        }

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

        if not resource.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reserve an inactive resource.",
            )

        if payload.attendees_count > resource.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendees count exceeds resource capacity.",
            )

        if self.reservations.has_conflict(payload.resource_id, payload.starts_at, payload.ends_at):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resource is already reserved for this period.",
            )

        reservation = self.reservations.create(payload)
        self.notification_client.send(
            NotificationPayload(
                reservation_id=reservation.id,
                user_email=user.email,
                message=f"Reservation confirmed for {resource.name}.",
                event_type="reservation_created",
            )
        )
        return reservation

    def update_reservation(self, reservation_id: int, payload: ReservationUpdate):
        reservation = self.get_reservation(reservation_id)
        if reservation.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled reservation.",
            )

        resource = reservation.resource
        if not resource.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reserve an inactive resource.",
            )

        starts_at = payload.starts_at or reservation.starts_at
        ends_at = payload.ends_at or reservation.ends_at
        attendees_count = payload.attendees_count or reservation.attendees_count
        title = payload.title if payload.title is not None else reservation.title
        purpose = payload.purpose if payload.purpose is not None else reservation.purpose

        if starts_at >= ends_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation end must be after start.",
            )

        if attendees_count > resource.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendees count exceeds resource capacity.",
            )

        if self.reservations.has_conflict(
            reservation.resource_id,
            starts_at,
            ends_at,
            exclude_reservation_id=reservation.id,
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resource is already reserved for this period.",
            )

        updated = self.reservations.update(
            reservation,
            starts_at,
            ends_at,
            title,
            purpose,
            attendees_count,
        )
        self.notification_client.send(
            NotificationPayload(
                reservation_id=updated.id,
                user_email=updated.user.email,
                message="Reservation updated.",
                event_type="reservation_updated",
            )
        )
        return updated

    def cancel_reservation(self, reservation_id: int):
        reservation = self.get_reservation(reservation_id)
        if reservation.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation is already cancelled.",
            )

        cancelled = self.reservations.cancel(reservation)
        self.notification_client.send(
            NotificationPayload(
                reservation_id=cancelled.id,
                user_email=cancelled.user.email,
                message="Reservation cancelled.",
                event_type="reservation_cancelled",
            )
        )
        return cancelled
