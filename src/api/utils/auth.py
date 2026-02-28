from datetime import datetime, timedelta, timezone
from jose import JWTError, ExpiredSignatureError, jwt
from typing import Any
from fastapi import Depends, Cookie, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from random import choices, shuffle
from string import digits, ascii_uppercase

from src.models.user import User
from src.core.config import settings
from src.core.exceptions import credentials_exception
from src.db.dependencies import get_db
from src.db.queries import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_verification_code() -> str:
    nums = choices(digits, k=4)
    letters = choices(ascii_uppercase, k=4)
    
    code = letters + nums
    shuffle(code)
    return ''.join(code)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        raise credentials_exception("Not a valid token")
    
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM, options={"verify_exp": True})
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception()
    
    except ExpiredSignatureError:
        raise credentials_exception("Token expired")
    except JWTError:
        raise credentials_exception()

    user = get_user_by_email(email, db)
    if user is None:
        raise credentials_exception()
    
    return user

def get_current_user_cookie(token: str = Cookie(None, alias="authorization"), db: Session = Depends(get_db)) -> User:
    try:
        return get_current_user(token, db)
    except HTTPException as e:
        raise credentials_exception(e.detail)