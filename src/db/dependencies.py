from typing import Generator, Any
from sqlalchemy.orm import Session

from src.db.session import SessionLocal

def get_db() -> Generator[Any | Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()