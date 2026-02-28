from pydantic import BaseModel
from datetime import datetime

class BillCreate(BaseModel):
    name: str
    amount: float
    due_date: datetime

class BillOut(BaseModel):
    id: int
    name: str
    amount: float
    due_date: datetime
    paid: bool

class BillPay(BaseModel):
    bill_id: int
    card_number: str