from pydantic import BaseModel, Field

class Saving_Account_creation(BaseModel):
    name: str
    goal: float = Field(..., gt=0, description='Goal must be positive')

class Saving_Account_out(BaseModel):
    id: int
    name: str
    balance: float
    goal: float
    remain: float

    class Config:
        from_attributes = True

class Saving_Account_TopUp(BaseModel):
    amount: float
    saving_account_id: int
    card_id: int

class Saving_Account_decrease(BaseModel):
    amount: float
    saving_account_id: int
    card_id: int

class Saving_Account_Delete(BaseModel):
    saving_account_id: int