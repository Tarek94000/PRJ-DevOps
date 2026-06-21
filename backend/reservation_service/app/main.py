from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.reservation_service.app.config import settings
from backend.reservation_service.app.controllers.routes import router
from backend.reservation_service.app.database import SessionLocal, create_schema
from backend.reservation_service.app.seed import seed_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_schema()
    if settings.demo_seed_enabled:
        with SessionLocal() as db:
            seed_demo_data(db)
    yield


app = FastAPI(title="Reservation Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
