from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.cards import TransferRequest, CardHistoryRequest, CardDelete
from src.db.dependencies import get_db
from src.api.utils.auth import get_current_user_cookie
from src.db.queries import get_cards
from src.services.cards import CardsService

router: APIRouter = APIRouter()

@router.get(
            "/{four_digits}",
            summary="Get single card by 4 last numbers",
            description="User must be logged into account to perform this option. Provide into route of endpoint last 4 digits of card to get the card. Example: url/card/0443",
            response_description="Returns all card information",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                500: {"description": "Function is not properly implemented, yet"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def get_card(four_digits: str, 
             user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    cards = get_cards(user, db)
    card = next((_card for _card in cards if _card.number[-4:] == four_digits), None)

    return card.json()

@router.post(
            "/create",
            summary="Card creation",
            description="User must be logged into account to perform this option. Creating card using information about user in database",
            response_description="Returns card data",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who card will be created has no wallet"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def create_card(user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        card = CardsService.create_card_logic(user, db)
        return card
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
                "/delete",
                summary="Deleting card",
                description="User must be logged into account to perform this option. Deleting card of user. Pass CardDelete body schema",
                response_description="",
                responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who card will be deleted has no wallet"},
                403: {"description": "Card balance is positive. Cannot delete card with funds on it"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def delete_card(card_delete: CardDelete, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        result = CardsService.delete_card_logic(user, card_delete.card_number, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
                "/transfer",
                summary="Transfering money from card to card",
                description="User must be logged into account to perform this option. Transfering money from card to card. Transfer operation will be added to history. Pass TransferRequest body schema",
                response_description="Returns how much money was transfered",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    406: {"description": "Reciever/Sender for who transfering operation will be called has no wallet"},
                    403: {"description": "Sender has no funds to perform operation"},
                    401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
                }
        )
def transfer_money(transfer: TransferRequest,
                   db: Session = Depends(get_db),
                   user: User = Depends(get_current_user_cookie)):
    CardsService.transfer_money_logic(transfer, user, db)

    return {
        f"Transferred {transfer.amount}"
    }

@router.get(
            "",
            summary="Get list of user\'s cards",
            description="User must be logged into account to perform this option. Getter for list of user cards. List contains of card data",
            response_description="Returns list of cards data",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who this operation will be called has no wallet"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def get_card_info(user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    return CardsService.get_card_info_logic(user, db)

@router.post(
            "/history",
            summary="Get transfer history",
            description="User must be logged into account to perform this option. Getter for list of transfers performed by user with n-card. Pass CardHistoryRequest body schema",
            response_description="Return list of transfers",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who this operation will be called has no wallet"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def get_transfer_history(
    request: CardHistoryRequest,
    user: User = Depends(get_current_user_cookie),
    db: Session = Depends(get_db)
):
    records = CardsService.get_transfer_history_logic(request.card_number, user, db)
    return records