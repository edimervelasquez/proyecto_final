import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import Config

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
