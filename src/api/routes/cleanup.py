from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.schemas.user import UserTemp as UnverifiedUser
from src.db.dependencies import get_db
from src.db.queries import get_expired_users

router: APIRouter = APIRouter()

@router.delete(
                "/cleanup-unverified",
                summary="Cleanup unverified users routine",
                description="Endpoint created to cleanup users in 24h timespan. Used in routine",
                response_description="Each time is called returns amount of users deleted"
        )
def cleanup_unverified_users(db: Session = Depends(get_db)):
    expiration_time = timedelta(hours=24)
    threshold = datetime.now() - expiration_time

    expired_users: list[UnverifiedUser] = get_expired_users(db, threshold)

    for user in expired_users:
        db.delete(user)

    db.commit()
    return {"message": f"Removed {len(expired_users)} expired unverified users."}