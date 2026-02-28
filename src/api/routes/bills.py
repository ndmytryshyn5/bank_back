from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.models.user import User
from src.schemas.bills import BillCreate, BillOut, BillPay
from src.db.dependencies import get_db
from src.api.utils.auth import get_current_user_cookie
from src.services.bills import BillsService

router: APIRouter = APIRouter()

@router.post(
            "/create",
            summary="Bill creation",
            description="User must be logged into account to perform this option. Pass the BillCreate body schema to create bill in database",
            response_description="Displaying the created bill",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who bill will be created has no wallet"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def create_bill(data: BillCreate, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        return BillsService.create_bill(user, data, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
            "",
            summary="Bill list getter",
            description="User must be logged into account to perform this option. Returns the list of bills which user created earlier. Displays current values of each user\'s bills",
            response_description="List of Bill. Check BillOut schema",
            response_model=List[BillOut],
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who bills will be shown has no wallet or actual bills"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
      
def get_user_bills(user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        return BillsService.get_user_bills(user, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
            "/pay",
            summary="Paying of the bill",
            description="User must be logged into account to perform this option. Bill paying is replicated into transfer history. Pass the BillPay body schema",
            response_description="Returns feedback information about card balance",
            responses={
                400: {"description": "Internal error accused by inprocessible data which crashed database"},
                406: {"description": "User for who bill will be paid has no wallet, card to pay or actual bills"},
                403: {"description": "Forbidden wallet action. Bill is paid off or card which tried to pay with has no funds"},
                401: {"description": "Credential exception. User is not logged or cookie is corrupted"}
            }
        )
def pay_bill(data: BillPay, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        return BillsService.pay_bill(user, data.bill_id, data.card_number, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))