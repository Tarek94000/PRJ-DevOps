from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.reservation_service.app import models


def seed_demo_data(db: Session) -> None:
    has_data = db.scalars(select(models.User.id).limit(1)).first() is not None
    if has_data:
        return

    user = models.User(name="Demo User", email="demo@example.com")
    resources = [
        models.Resource(
            name="Salle Innovation",
            location="Campus Paris",
            capacity=12,
            resource_type="meeting-room",
            description="Salle equipee pour reunions projet et soutenances.",
            equipment=["wifi", "screen", "whiteboard"],
        ),
        models.Resource(
            name="Lab DevOps",
            location="Campus Paris",
            capacity=8,
            resource_type="lab",
            description="Espace de demonstration pour CI/CD et conteneurs.",
            equipment=["wifi", "docker", "projector"],
        ),
    ]
    db.add(user)
    db.add_all(resources)
    db.flush()

    starts_at = datetime.now(UTC).replace(microsecond=0) + timedelta(days=1, hours=2)
    db.add(
        models.Reservation(
            user_id=user.id,
            resource_id=resources[0].id,
            title="Demo pipeline CI/CD",
            purpose="Reservation de demonstration apres lancement Docker Compose.",
            attendees_count=4,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
        )
    )
    db.commit()
