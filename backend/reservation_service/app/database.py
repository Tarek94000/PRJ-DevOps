from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.reservation_service.app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_schema() -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_columns()


def add_missing_columns() -> None:
    inspector = inspect(engine)
    if "resources" in inspector.get_table_names():
        resource_columns = {column["name"] for column in inspector.get_columns("resources")}
        add_columns(
            "resources",
            resource_columns,
            {
                "capacity": "INTEGER NOT NULL DEFAULT 1",
                "resource_type": "VARCHAR(60) NOT NULL DEFAULT 'room'",
                "description": "TEXT NOT NULL DEFAULT ''",
                "equipment": json_column_sql(),
                "is_active": boolean_column_sql(default=True),
            },
        )

    inspector = inspect(engine)
    if "reservations" in inspector.get_table_names():
        reservation_columns = {column["name"] for column in inspector.get_columns("reservations")}
        add_columns(
            "reservations",
            reservation_columns,
            {
                "title": "VARCHAR(160) NOT NULL DEFAULT 'Reservation'",
                "purpose": "TEXT NOT NULL DEFAULT ''",
                "attendees_count": "INTEGER NOT NULL DEFAULT 1",
                "created_at": datetime_column_sql(),
                "updated_at": datetime_column_sql(),
            },
        )


def add_columns(table_name: str, existing_columns: set[str], columns: dict[str, str]) -> None:
    with engine.begin() as connection:
        for column_name, definition in columns.items():
            if column_name not in existing_columns:
                statement = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"
                connection.execute(text(statement))


def json_column_sql() -> str:
    if engine.dialect.name == "postgresql":
        return "JSON NOT NULL DEFAULT '[]'"
    return "JSON NOT NULL DEFAULT '[]'"


def boolean_column_sql(default: bool) -> str:
    if engine.dialect.name == "postgresql":
        return f"BOOLEAN NOT NULL DEFAULT {'TRUE' if default else 'FALSE'}"
    return f"BOOLEAN NOT NULL DEFAULT {1 if default else 0}"


def datetime_column_sql() -> str:
    if engine.dialect.name == "postgresql":
        return "TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP"
    return "DATETIME NOT NULL DEFAULT '1970-01-01 00:00:00'"
