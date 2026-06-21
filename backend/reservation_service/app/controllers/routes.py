from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.reservation_service.app.database import get_db
from backend.reservation_service.app.schemas import (
    DashboardRead,
    ReservationCreate,
    ReservationRead,
    ReservationUpdate,
    ResourceCreate,
    ResourceRead,
    ResourceUpdate,
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


@router.get("/users", response_model=list[UserRead])
def list_users(service: ReservationServiceDep):
    return service.list_users()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, service: ReservationServiceDep):
    return service.get_user(user_id)


@router.post("/resources", response_model=ResourceRead, status_code=201)
def create_resource(payload: ResourceCreate, service: ReservationServiceDep):
    return service.create_resource(payload)


@router.get("/resources", response_model=list[ResourceRead])
def list_resources(service: ReservationServiceDep):
    return service.list_resources()


@router.get("/resources/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: int, service: ReservationServiceDep):
    return service.get_resource(resource_id)


@router.patch("/resources/{resource_id}", response_model=ResourceRead)
def update_resource(resource_id: int, payload: ResourceUpdate, service: ReservationServiceDep):
    return service.update_resource(resource_id, payload)


@router.delete("/resources/{resource_id}", response_model=ResourceRead)
def deactivate_resource(resource_id: int, service: ReservationServiceDep):
    return service.deactivate_resource(resource_id)


@router.post("/reservations", response_model=ReservationRead, status_code=201)
def create_reservation(payload: ReservationCreate, service: ReservationServiceDep):
    return service.create_reservation(payload)


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(service: ReservationServiceDep):
    return service.list_reservations()


@router.get("/reservations/{reservation_id}", response_model=ReservationRead)
def get_reservation(reservation_id: int, service: ReservationServiceDep):
    return service.get_reservation(reservation_id)


@router.patch("/reservations/{reservation_id}", response_model=ReservationRead)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    service: ReservationServiceDep,
):
    return service.update_reservation(reservation_id, payload)


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_reservation(reservation_id: int, service: ReservationServiceDep):
    return service.cancel_reservation(reservation_id)


@router.get("/dashboard", response_model=DashboardRead)
def dashboard(service: ReservationServiceDep):
    return service.dashboard()
