from os import environ
from typing import Any, Generator
from sqlmodel import create_engine, Session
from schemas import SQLModel
from dotenv import load_dotenv

load_dotenv()

ENV = environ.get("ENV")
DB_NAME = environ.get("DB_NAME")
DB_USER = environ.get("DB_USER")
DB_HOSTNAME = environ.get("DB_HOSTNAME")
DB_PWD = environ.get("DB_PWD")

db_url = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOSTNAME}/{DB_NAME}"
engine = create_engine(db_url, echo=True if ENV == "dev" else False)


def get_db() -> Generator[Session, Any, None]:
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
