from sqlalchemy import Column, Integer, ForeignKey, Float, String
from sqlalchemy.orm import relationship

from src.db.base import Base

class Saving_account(Base):
    __tablename__ = 'saving_accounts'

    id: Column = Column(Integer, primary_key=True)
    name: Column = Column(String, nullable=False)
    balance: Column = Column(Float, default=200.0)
    goal: Column = Column(Float)

    wallet_id: Column = Column(Integer, ForeignKey('wallets.id'), nullable=False)

    wallet = relationship("Wallet", back_populates="saving_account")