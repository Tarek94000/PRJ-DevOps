from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.reservation_service.app.database import get_db
from backend.reservation_service.app.schemas import (
    ReservationCreate,
    ReservationRead,
    ResourceCreate,
    ResourceRead,
    UserCreate,
    UserRead,
)
from backend.reservation_service.app.services.reservation_service import ReservationService

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


def get_service(db: DbSession) -> ReservationService:
    return ReservationService(db)


ReservationServiceDep = Annotated[ReservationService, Depends(get_service)]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, service: ReservationServiceDep):
    return service.create_user(payload)


@router.post("/resources", response_model=ResourceRead, status_code=201)
def create_resource(payload: ResourceCreate, service: ReservationServiceDep):
    return service.create_resource(payload)


@router.get("/resources", response_model=list[ResourceRead])
def list_resources(service: ReservationServiceDep):
    return service.list_resources()


@router.post("/reservations", response_model=ReservationRead, status_code=201)
def create_reservation(payload: ReservationCreate, service: ReservationServiceDep):
    return service.create_reservation(payload)


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(service: ReservationServiceDep):
    return service.list_reservations()


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_reservation(reservation_id: int, service: ReservationServiceDep):
    return service.cancel_reservation(reservation_id)
