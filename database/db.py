import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "ticket_to_ride.db"

# Permite usar una base distinta (por ejemplo, en los tests) sin tocar la real.
DB_PATH = Path(os.environ.get("TICKET_TO_RIDE_DB", DEFAULT_DB_PATH)).resolve()
DATABASE_URL = os.environ.get("DATABASE_URL") or f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase):
    pass


db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
