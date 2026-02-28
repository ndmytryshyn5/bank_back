from sqlalchemy.orm import Session

from src.models.bills import Bills
from src.db.queries import get_wallet, get_card_by_number, get_bill_by_id
from src.core.exceptions import user_not_found, card_not_found, forbidden_wallet_action
from src.models.wallet_history import TransferHistory, TransactionType

class BillsService:
    @staticmethod
    def create_bill(user, data, db: Session):
        wallet = get_wallet(user, db)
        if not wallet:
            raise user_not_found

        bill = Bills(
            name=data.name,
            amount=data.amount,
            due_date=data.due_date,
            wallet_id=wallet.id
        )

        db.add(bill)
        db.commit()
        db.refresh(bill)

        return {
            "id": bill.id,
            "name": bill.name,
            "amount": bill.amount,
            "due_date": bill.due_date,
            "paid": bill.paid
        }

    @staticmethod
    def get_user_bills(user, db: Session):
        wallet = get_wallet(user, db)
        if not wallet:
            raise user_not_found

        bills = db.query(Bills).filter(Bills.wallet_id == wallet.id).all()

        return bills

    @staticmethod
    def pay_bill(user, bill_id: int, card_number: str, db: Session):
        wallet = get_wallet(user, db)
        bill = get_bill_by_id(user, bill_id, db)
        card = get_card_by_number(user, card_number, db)

        if not wallet or not bill or not card:
            raise user_not_found

        if not card:
            raise card_not_found

        if bill.paid:
            raise forbidden_wallet_action("Bill already paid")

        if card.balance < bill.amount:
            raise forbidden_wallet_action("Not enough funds")

        card.balance -= bill.amount
        bill.paid = True

        history_record = TransferHistory(
            transfer_type=TransactionType.BILL,
            from_user_card_number=card.number,
            from_user=f"{card.cardholder_name} {card.cardholder_surname}",
            to_user_card_number=None,
            to_user=f"Bill - {bill.name}",
            amount=bill.amount
        )

        db.add(history_record)

        db.commit()
        db.refresh(bill)
        db.refresh(card)

        return {
            "status": "paid",
            "bill_id": bill.id,
            "remaining_card_balance": card.balance
        }
