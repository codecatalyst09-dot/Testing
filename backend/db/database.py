from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

from backend.utils.paths import get_storage_dir

# Local SQLite storage path
DB_DIR = get_storage_dir()
SQL_DB_PATH = DB_DIR / "analyzer.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQL_DB_PATH.as_posix()}"

# Note: Check_same_thread=False is needed for SQLite with FastAPI multi-threading
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.db import models  # noqa
    Base.metadata.create_all(bind=engine)

# Auto-initialize tables on import
init_db()
