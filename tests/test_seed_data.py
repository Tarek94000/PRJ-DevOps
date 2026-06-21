from backend.reservation_service.app import models
from backend.reservation_service.app.seed import seed_demo_data


def test_seed_demo_data_populates_empty_database_once(db_session):
    seed_demo_data(db_session)
    seed_demo_data(db_session)

    assert db_session.query(models.User).count() == 1
    assert db_session.query(models.Resource).count() == 2
    assert db_session.query(models.Reservation).count() == 1
    assert db_session.query(models.User).first().email == "demo@example.com"
