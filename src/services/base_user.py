from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from typing import Any
from datetime import datetime, timezone, timedelta

from src.models.user import User
from src.schemas.user import UserLogin
from src.db.queries import get_user_by_email, validate_code
from src.api.utils.auth import create_access_token
from src.core.exceptions import credentials_exception
from src.core.config import settings
from src.api.utils.mail import send_email, EmailType
from src.api.utils.auth import create_verification_code

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BaseUserService:
    @staticmethod
    def validate(user_data: UserLogin, db: Session) -> User:
        if not user_data.email or not user_data.password:
            raise credentials_exception()

        user: User = get_user_by_email(user_data.email, db)

        if not user or not pwd_context.verify(user_data.password, user.hashed_password):
            raise credentials_exception()
        
        return user

    @staticmethod
    def login(email: str, db: Session) -> JSONResponse:        
        token = create_access_token({"sub": email})
        resp = JSONResponse({"message": "Access granted"})
        
        resp.set_cookie(
                            key="authorization",
                            value=token,
                            httponly=True,
                            secure=True,
                            samesite="none",
                            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60,
                            path="/"
                        )

        return resp
    
    @staticmethod
    def twofa_confirm(user_data: UserLogin, db: Session) -> JSONResponse:
        user: User = get_user_by_email(user_data.email, db)

        try:
            if not user_data.twofa_code or not validate_code(user, user_data.twofa_code):
                raise credentials_exception("Not valid code")
        except:
            raise credentials_exception("Not valid code or user is not requested")

        user.last_2fa_code = None
        user.expires_at_2fa = None

        db.commit()
        db.refresh(user)

        return BaseUserService.login(user_data.email, db)

    @staticmethod
    def twofa_request(user_data: UserLogin, db: Session) -> dict[str, Any]:
        user: User = BaseUserService.validate(user_data, db)

        user.last_2fa_code = create_verification_code()
        user.expires_at_2fa = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        send_email(user_data.email, "Login 2FA code", EmailType.TWOFA, code=user.last_2fa_code)

        return {"message": "Request sended"}
    
    @staticmethod
    def logout() -> JSONResponse:
        response = JSONResponse({"message": "Goodbye"})
        response.delete_cookie("authorization")
        return response