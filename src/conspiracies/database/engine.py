from pathlib import Path

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from conspiracies.database.models import Base


def get_engine(filepath: Path):
    engine = create_engine("sqlite:///" + filepath.as_posix())
    return engine


def setup_database(engine: Engine):
    Base.metadata.create_all(engine)


def get_session(engine: Engine = None) -> Session:
    session = Session(bind=engine)
    return session
