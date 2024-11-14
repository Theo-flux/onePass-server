from os import environ
from typing import Any, Generator
from sqlmodel import create_engine, Session
from config.env import OnepassEnvs
from schemas import SQLModel

ENV = OnepassEnvs.get("ENV")
DB_NAME = OnepassEnvs.get("DB_NAME")
DB_USER = OnepassEnvs.get("DB_USER")
DB_HOSTNAME = OnepassEnvs.get("DB_HOSTNAME")
DB_PWD = OnepassEnvs.get("DB_PWD")

db_url = f"postgresql://{DB_USER}:{DB_PWD}@{DB_HOSTNAME}/{DB_NAME}"
engine = create_engine(db_url, echo=True if ENV == "dev" else False)


def get_db() -> Generator[Session, Any, None]:
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
