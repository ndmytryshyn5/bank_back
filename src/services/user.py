from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timezone
from urllib.parse import urljoin, urlencode
from secrets import token_urlsafe
from typing import Any

from src.schemas.user import UserCreate, UserTemp, UserPasswordReset
from src.models.user import User, UnverifiedUser
from src.models.wallet import Wallet
from src.db.queries import is_user_existing, is_code_valid, get_unverified_user
from src.api.utils.auth import create_verification_code
from src.api.utils.mail import send_email, EmailType
from src.models.cards import Card
from src.db.queries import get_cards, get_user_by_reset_token, validate_token
from src.core.exceptions import user_exists_exception, code_verification_exception, credentials_exception, bad_requset
from src.services.base_user import BaseUserService
from src.core.traceback import traceBack, TrackType
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(BaseUserService):
    @staticmethod
    def check_availability(payload: dict[str, str], db: Session) -> dict[str, bool]:
        fields_to_check = {
            "email": [User.email, UnverifiedUser.email],
            "phone_number": [User.phone_number, UnverifiedUser.phone_number],
            "social_security": [User.social_security, UnverifiedUser.social_security],
        }

        result = {}
        for field, value in payload.items():
            if field in fields_to_check:
                result[field] = True
                for column in fields_to_check[field]:
                    model_class = column.class_
                    exists = db.query(model_class).filter(column == value).first()
                    if exists:
                        result[field] = False
                        break
        return result

    @staticmethod
    def register(user: UserTemp, db: Session):
        if is_user_existing(user, db):
            raise user_exists_exception

        verification_code = create_verification_code()
        temp_user: UnverifiedUser = UnverifiedUser(
            email=user.email,
            social_security=user.social_security,
            phone_number=user.phone_number,
            code=verification_code
        )
        
        db.add(temp_user)

        try:
            send_email(temp_user.email, "Email Verification", EmailType.REGISTRATION, code=verification_code)
        except Exception as e:
            traceBack(f"{e}", type=TrackType.ERROR)
            db.rollback()
            raise bad_requset()

        db.commit()
        db.refresh(temp_user)

    @staticmethod
    def verify_email(user_data: UserCreate, db: Session):
        if not is_code_valid(user_data.email, user_data.verification_code, db):
            raise code_verification_exception

        temp_user = get_unverified_user(user_data.email, db)

        new_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone_number=user_data.phone_number,
            date_of_birth=user_data.date_of_birth,
            social_security=user_data.social_security,
            address=user_data.address,
            city=user_data.city,
            state=user_data.state,
            post_code=user_data.post_code,
            hashed_password=pwd_context.hash(user_data.password)
        )

        db.add(new_user)
        db.delete(temp_user)
        db.commit()

        db.refresh(new_user)
        
        new_wallet: Wallet = Wallet(
            user_id=new_user.id
        )

        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)

    @staticmethod
    def get_user_base_data(user: User, db: Session) -> dict[str, Any]:
        if not user:
            raise credentials_exception()
        
        cards: list[Card] = get_cards(user, db)

        data = {
            "name": user.first_name,
            "surname": user.last_name,
            "cards": [
                {
                    "balance": card.balance,
                    "last4": card.number[-4:]
                }
                for card in cards
            ]
        }

        return data
    
    @staticmethod
    def reset_password_request(user_reset: UserTemp, db: Session) -> dict[str, Any]:
        user: User = db.query(User).filter(User.email == user_reset.email,
                                     User.social_security == user_reset.social_security,
                                     User.phone_number == user_reset.phone_number).first()

        if user is None:
            raise credentials_exception()
        
        reset_token: str = token_urlsafe(32)

        while get_user_by_reset_token(reset_token, db) != None:
            reset_token: str = token_urlsafe(32)
        
        user.reset_token = reset_token
        user.reset_token_created_at = datetime.now(timezone.utc)
        base_url: str = None

        if settings.IS_DEPLOYED:
            base_url = settings.ORIGINS[-1]
        else:
            base_url = settings.ORIGINS[0]
            
        link = urljoin(base_url, "/reset") + "?" + urlencode({"token": user.reset_token})

        send_email(user.email, "Password reset", EmailType.PASSWORD_RESET, link=link)

        db.commit()
        db.refresh(user)

        return {"message": "Email sended"}

    @staticmethod
    def reset_password_confirm(password_form: UserPasswordReset, db: Session) -> dict[str, Any]:
        user: User = get_user_by_reset_token(password_form.token, db)
        
        if not validate_token(user, db):
            raise credentials_exception("Reset token is not valid")

        user.hashed_password = pwd_context.hash(password_form.new_password)
        user.reset_token = None
        user.reset_token_created_at = None
        db.commit()
        db.refresh(user)

        return {"message": "Password changed"}