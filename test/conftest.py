import os
import shutil
import tempfile
from pathlib import Path

import pytest

# La base de los tests se configura antes de importar la aplicación.
TEST_DIR = Path(tempfile.mkdtemp(prefix="ticket_to_ride_test_"))
TEST_DB = TEST_DIR / "test.db"
os.environ["TICKET_TO_RIDE_DB"] = str(TEST_DB)

from app import create_app  # noqa: E402
from database.db import Base, db_session, engine  # noqa: E402
from database.seed import cargar_datos_prueba  # noqa: E402


@pytest.fixture(scope="session")
def app():
    application = create_app()
    application.config.update(TESTING=True)
    yield application

    db_session.remove()
    engine.dispose()
    shutil.rmtree(TEST_DIR, ignore_errors=True)


@pytest.fixture()
def db(app):
    """Reinicia la base antes de cada test y carga los datos de prueba."""
    db_session.remove()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    cargar_datos_prueba()
    yield
    db_session.remove()


@pytest.fixture()
def client(db, app):
    with app.test_client() as test_client:
        yield test_client
