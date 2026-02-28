from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from src.db.base import Base

class TransactionType(Enum):
    TRANSFER = 0
    INCOME = 1
    PURCHASE = 2
    BILL = 3
    SAVINGS_TOPUP = 4
    SAVINGS_WITHDRAW = 5

class TransferHistory(Base):
    __tablename__ = "transfer_history"

    id = Column(Integer, primary_key=True, index=True)
    transfer_type = Column(SQLEnum(TransactionType), default=TransactionType.PURCHASE)
    from_user_card_number = Column(String)
    from_user = Column(String)
    to_user_card_number = Column(String)
    to_user = Column(String)
    amount = Column(Float)
    time = Column(DateTime, default=datetime.now)
