from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.savings import Saving_Account_creation, Saving_Account_out, Saving_Account_TopUp, Saving_Account_Delete
from src.db.dependencies import get_db
from src.api.utils.auth import get_current_user_cookie
from src.services.savings import SavingsService
from typing import List

router: APIRouter = APIRouter()
@router.post(
                "/create",
                summary="Creation of saving account",
                description="User must be logged into account to perform this option. Setting goal for users desire. Pass Saving_Account_creation body scheme",
                response_description="Returns saving data on success",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"},
                    406: {"description": "User for who this operation will be called has no wallet"}
                }
            )
def create_saving_account(data: Saving_Account_creation, db: Session = Depends(get_db), user: User = Depends(get_current_user_cookie)):
    try:
        saving_account = SavingsService.create_saving_account(user, data, db)
        return saving_account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
                "",
                response_model=List[Saving_Account_out],
                summary="Getter for savings",
                description="User must be logged into account to perform this option.",
                response_description="Returns list of Saving_Account_out. Check schema",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"},
                    406: {"description": "User for who this operation will be called has no wallet or saving account"}
                }
            )
def get_saving_accounts(user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        return SavingsService.get_user_saving_accounts(user, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
                "/topUp",
                summary="Toping up savings",
                description="User must be logged into account to perform this option. Used to topping up savings. Topping up is mirrored into transfer history. Pass Saving_Account_TopUp body scheme",
                response_description="",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"},
                    403: {"description": "Forbidden wallet action. Savings are not existed or card which tried to pay with has no funds"},
                    406: {"description": "User for who this operation will be called has no wallet or saving account"}
                }
            )
def topUp_saving_account(data: Saving_Account_TopUp, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):

    try:
        return SavingsService.add_funds(data, user, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
                "/decrease",
                summary="Decreasing savings",
                description="User must be logged into account to perform this option. Taking funds from savings to card. Pass Saving_Account_TopUp body scheme",
                response_description="",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"},
                    403: {"description": "Forbidden wallet action. Card is not exists or savings which tried to decrease of has no funds"},
                    406: {"description": "User for who this operation will be called has no wallet or saving account"}
                }
            )
def decrease_saving_account(data: Saving_Account_TopUp, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):

    try:
        return SavingsService.take_funds(data, user, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
                "/delete",
                summary="Deletes savings account",
                description="User must be logged into account to perform this option. Deletes savings account. Pass Saving_Account_Delete body schema",
                response_description="Returns id and status of deleted saving account",
                responses={
                    400: {"description": "Internal error accused by inprocessible data which crashed database"},
                    401: {"description": "Account is not exists, user not logged into account or provided data is incorrect"},
                    403: {"description": "Forbidden wallet action. Savings has positive amount of funds or savings is not exists"},
                    406: {"description": "User for who this operation will be called has no wallet"}
                }
            )
def delete_saving_account(data: Saving_Account_Delete, user: User = Depends(get_current_user_cookie), db: Session = Depends(get_db)):
    try:
        return SavingsService.delete_saving_account_logic(user, data.saving_account_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))