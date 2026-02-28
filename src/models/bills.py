from sqlalchemy import Column, Boolean, Integer, Float, DateTime, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from src.db.base import Base

class Bills(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid = Column(Boolean, default=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)