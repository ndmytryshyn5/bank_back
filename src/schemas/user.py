from datetime import date
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: date
    social_security: str
    address: str
    city: str
    state: str
    post_code: str
    password: str
    verification_code: str

class UserTemp(BaseModel):
    email: EmailStr
    phone_number: str
    social_security: str

class UserLogin(BaseModel):
    email: str
    password: str | None = None
    twofa_code: str | None = None

class UserPasswordReset(BaseModel):
    token: str
    new_password: str