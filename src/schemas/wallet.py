from pydantic import BaseModel, EmailStr, Field
from src.schemas.token import Token

class WalletGet(BaseModel):
    balance: float
    token: Token

class TransferRequest(BaseModel):
    from_email: EmailStr
    to_email: EmailStr
    amount: float = Field(..., gt=0, description="Amount must be positive")