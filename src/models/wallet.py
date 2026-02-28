from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base

class Wallet(Base):
    __tablename__ = 'wallets'

    id: Column = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='wallets')
    cards = relationship("Card", back_populates="wallet")
    saving_account = relationship("Saving_account", back_populates="wallet")