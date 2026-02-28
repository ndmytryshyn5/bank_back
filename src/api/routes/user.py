from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.schemas.user import UserCreate, UserLogin, UserTemp, UserPasswordReset
from src.db.dependencies import get_db
from src.services.user import UserService
from src.models.user import User
from src.api.utils.auth import get_current_user_cookie

router: APIRouter = APIRouter()

@router.post(
                "/register",
                summary="Pre-registration form",
                description="Form to create temp user before verification of email. Used to check whenever account data is unique. Check UserTemp schema. Pass UserTemp body schema",
                response_description="Returns positive status of pre-registration",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database or SMTP server"},
                    409: {"description": "Conflict. The main unique data is already exists for another user"},
                }
            )
def register_user(user: UserTemp, db: Session = Depends(get_db)):
    UserService.register(user, db)
    return {"message": "Mail has been send"}

@router.post(
                "/verify-email",
                summary="Full account registration",
                description="Account being created with full provided information about user. Additionally to user information, verification code from email is passed. Check UserCreate schema. Pass UserCreate body schema",
                response_description="Returns positive status of registration and cookie for first account access",
                responses={
                    406: {"description": "Bad verification code or this account is not needed for account"}
                }
            )
def verify_email(user: UserCreate, db: Session = Depends(get_db)):
    UserService.verify_email(user, db)
    user_data = UserLogin(email=user.email, password=user.password)
    return UserService.login(user_data.email, db)

@router.post(
                "/2fa/request",
                summary="First step for login",
                description="First step for login to send verification code. Pass email and password fields of UserLogin body schema",
                response_description="Returns positive status of first step",
                responses={
                    401: {"description": "Account is not exists or provided data is incorrect"}
                }
            )
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return UserService.twofa_request(user_data, db)

@router.post(
                "/2fa/confirm",
                summary="Last step for login",
                description="Last step for login to end login process. Pass email and twofa_code fields of UserLogin body schema",
                response_description="Returns positive status of login and cookie for account access",
                responses={
                    401: {"description": "Account is not exists or provided data is incorrect"}
                }
            )
def twofa_confirm(user_data: UserLogin, db: Session = Depends(get_db)):
    return UserService.twofa_confirm(user_data, db)

@router.get(
                "/me",
                summary="Base user data",
                description="User must be logged into account to perform this option.",
                response_description="Returns base user data of user. Name and balance",
                responses={
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"}
                }
            )
def get_user_base_data(user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    return UserService.get_user_base_data(user, db)

@router.post(
                "/reset",
                summary="Reset password request",
                description="Requesting reset password for account. To confirm it\'s actuall owner pass UserTemp body schema",
                response_description="Returns positive status of sending reset link",
                responses={
                    401: {"description": "Account is not exists or provided data is incorrect"}
                }
            )
def reset_password_request(user_reset: UserTemp, db: Session = Depends(get_db)):
    return UserService.reset_password_request(user_reset, db)

@router.patch(
                "/reset",
                summary="Reset password confirm",
                description="Confirmation of password resetting. Pass UserPasswordReset body schema",
                response_description="Returns positive status of process",
                responses={
                    401: {"description": "Account is not requests password reset or token is incorrect"}
                }
            )
def reset_password_confirm(password_form: UserPasswordReset, db: Session = Depends(get_db)):
    return UserService.reset_password_confirm(password_form, db)

@router.post(
                "/logout",
                summary="Log out",
                description="User must be logged into account to perform this option.",
                response_description="Deleting the cookie"
            )
def logout():
    return UserService.logout()