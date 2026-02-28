from pydantic import BaseModel, constr, Field

class CardCreate(BaseModel):
    id: int
    cardholder_name: str
    cardholder_surname: str
    number: constr(min_length=13, max_length=19)
    expiration_date: str
    cvv: constr(min_length=3, max_length=4)

class TransferRequest(BaseModel):
    from_card_number: str
    to_card_number: str
    amount: float = Field(..., gt=0, description="Amount must be positive")

class CardHistoryRequest(BaseModel):
    card_number: str

class CardDelete(BaseModel):
    card_number: str