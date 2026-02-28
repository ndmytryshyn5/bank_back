from random import randint
from datetime import datetime, timedelta, timezone
from sqlalchemy import exists
from sqlalchemy.orm import Session

from src.db.queries import get_wallet
from src.models.user import User
from src.schemas.cards import TransferRequest
from src.models.cards import Card
from src.models.wallet_history import TransferHistory, TransactionType
from src.core.exceptions import user_not_found, forbidden_wallet_action, card_not_found, cannot_delete_card_with_balance
from src.db.queries import get_cards, get_user_by_card_number, get_card_transfer_history_records, get_card_by_number
from src.core.traceback import traceBack, TrackType

def generate_card_number(db: Session):
    while True:
        number = ''.join(str(randint(0, 9)) for _ in range(16))
        if not get_user_by_card_number(number, db):
            return number
    
def generate_cvv():
    return ''.join(str(randint(0, 9)) for _ in range(3))

def generate_expiration_date():
    future_date = datetime.now(timezone.utc) + timedelta(days=365 * 5)
    return future_date.strftime("%m/%y")

class CardsService:
    @staticmethod
    def create_card_logic(user: User, db: Session) -> dict:
        wallet = get_wallet(user, db)
        if not wallet:
            raise user_not_found

        card_number = generate_card_number(db)
        card_cvv = generate_cvv()
        card_expiry = generate_expiration_date()

        card = Card(
            wallet_id = wallet.id,
            cardholder_name=user.first_name,
            cardholder_surname=user.last_name,
            number = card_number,
            expiration_date = card_expiry,
            cvv = card_cvv
        )

        db.add(card)
        db.commit()
        db.refresh(card)

        return card.json()

    @staticmethod
    def delete_card_logic(user: User, card_number:str, db: Session) -> dict:
        card = get_card_by_number(user, card_number, db)
        if not card:
            raise card_not_found

        if card.balance > 0:
            raise cannot_delete_card_with_balance

        db.delete(card)
        db.commit()

        return{
            "status": "deleted",
            "card_number": card_number
        }


    @staticmethod
    def transfer_money_logic(transfer: TransferRequest, user: User, db: Session):
        receiver = get_user_by_card_number(transfer.to_card_number, db)
        if not receiver:
            raise user_not_found

        sender_card: Card = get_card_by_number(user, transfer.from_card_number, db)
        receiver_card: Card = get_card_by_number(receiver, transfer.to_card_number, db)

        if not sender_card or not receiver_card:
            raise card_not_found

        if sender_card.balance < transfer.amount:
            raise forbidden_wallet_action("Not enough funds")

        sender_card.balance -= transfer.amount
        receiver_card.balance += transfer.amount

        history_record = TransferHistory(
            transfer_type=TransactionType.TRANSFER,
            from_user_card_number=sender_card.number,
            from_user=f"{sender_card.cardholder_name} {sender_card.cardholder_surname}",
            to_user_card_number=receiver_card.number,
            to_user=f"{receiver_card.cardholder_name} {receiver_card.cardholder_surname}",
            amount=transfer.amount
        )

        db.add(history_record)
        db.commit()
        db.refresh(sender_card)
        db.refresh(receiver_card)

        return history_record

    @staticmethod
    def get_card_info_logic(user: User, db: Session) -> list[dict]:
        cards = get_cards(user, db)
        if not cards:
            raise user_not_found

        return [
            {
                "card_id": card.id,
                "number": card.number,
                "cardholder_name": card.cardholder_name,
                "cardholder_surname": card.cardholder_surname,
                "expiration_date": card.expiration_date,
                "cvv": card.cvv,
                "balance": card.balance
            }
            for card in cards
        ]

    @staticmethod
    def get_transfer_history_logic(card_number: str, user: User, db: Session) -> dict[str, list]:
        card = get_card_by_number(user, card_number, db)
        if not card:
            raise card_not_found

        records = get_card_transfer_history_records(card, db)

        result = []
        for record in records:
            direction = (
                "out" if record.from_user_card_number == card.number else "in"
            )

            result.append({
                "direction": direction,
                "from": record.from_user,
                "from_card_number": record.from_user_card_number,
                "to": record.to_user,
                "to_card_number": record.to_user_card_number,
                "transfer_type": record.transfer_type.name,
                "amount": record.amount,
                "time": record.time.isoformat()
            })

        return {"history": result}