import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session as ORM
import random
import string

from src.core.config import settings
from src.core.traceback import traceBack

from src.models.user import User, UnverifiedUser
from src.models.wallet import Wallet
from src.models.wallet_history import TransferHistory
from src.models.bills import Bills
from src.models.cards import Card
from src.models.savings import Saving_account 

def change_balance(card_id: int, balance: int, db: ORM):
    card: Card = db.query(Card).filter(Card.id == card_id).first()

    assert card is not None, "Card not found in DB"
    
    card.balance = balance
    db.commit()
    db.refresh(card)

    assert card.balance == balance, "Card balance was not changed"
    traceBack(f"Card[{card_id}] balance changed to {balance}")

def random_email():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"testuser_{suffix}@localhost.me"

def random_phone(db: ORM):
    while True:
        number = "+22" + ''.join(random.choices(string.digits, k=9))
        if not db.query(User).filter(User.phone_number == number).first() and \
        not db.query(UnverifiedUser).filter(UnverifiedUser.phone_number == number).first():
            break

    return number

def random_ssn(db: ORM):
    while True:
        number = ''.join(random.choices(string.digits, k=8))
        if not db.query(User).filter(User.social_security == number).first() and \
        not db.query(UnverifiedUser).filter(UnverifiedUser.social_security == number).first():
            break

    return number

def get_verification_code(email: str, db: ORM):
    user = db.query(UnverifiedUser).filter(UnverifiedUser.email == email).first()
    assert user and user.code, "No code found"
    return user.code

def get_reset_token(email: str, db: ORM):
    user = db.query(User).filter(User.email == email).first()
    assert user and user.reset_token, "No reset token found"
    return user.reset_token

def get_2fa_code(email: str, db: ORM):
    user = db.query(User).filter(User.email == email).first()
    assert user and user.last_2fa_code, "No 2FA code found"
    return user.last_2fa_code

def clean_test_user(user_data: dict, db: ORM):
    print()
    user: User = db.query(User).filter(User.email == user_data["email"], 
                                 User.social_security == user_data["social_security"], 
                                 User.phone_number == user_data["phone_number"], 
                                 ).first()
    
    assert user is not None, "User is None"
    traceBack(f"Cleaning up test user {user.email}")

    wallet: Wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
    assert wallet is not None, "Wallet is None"

    db.query(Card).filter(Card.wallet_id == wallet.id).delete()
    db.query(Saving_account).filter(Saving_account.wallet_id == wallet.id).delete()
    db.query(Bills).filter(Bills.wallet_id == wallet.id).delete()
    
    db.delete(wallet)
    db.delete(user)
    db.commit()