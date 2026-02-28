from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, text, Boolean
from sqlalchemy.orm import relationship
from src.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Column = Column(Integer, primary_key=True, index=True)
    first_name: Column = Column(String, nullable=False)
    last_name: Column = Column(String, nullable=False)
    email: Column = Column(String, unique=True, nullable=False, index=True)
    phone_number: Column = Column(String, unique=True, nullable=False, index=True)
    date_of_birth: Column = Column(Date, nullable=False)
    social_security: Column = Column(String, unique=True, nullable=False)
    address: Column = Column(String, nullable=False)
    city: Column = Column(String, nullable=False)
    state: Column = Column(String, nullable=False)
    post_code: Column = Column(String, nullable=False)
    hashed_password: Column = Column(String, nullable=False)
    created_at: Column = Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    last_2fa_code: Column = Column(String, nullable=True, default=None)
    expires_at_2fa: Column = Column(TIMESTAMP(timezone=True), nullable=True, default=None)

    reset_token: Column = Column(String, nullable=True, default=None)
    reset_token_created_at: Column = Column(TIMESTAMP(timezone=True), nullable=True, default=None)

    wallets = relationship("Wallet", back_populates="user")

class UnverifiedUser(Base):
    __tablename__ = "unverified_users"

    id: Column = Column(Integer, primary_key=True, index=True)
    email: Column = Column(String, unique=True, nullable=False, index=True)
    phone_number: Column = Column(String, unique=True, nullable=False, index=True)
    social_security: Column = Column(String, unique=True, nullable=False)
    code: Column = Column(String, nullable=False)

    created_at: Column = Column("created_at", TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))