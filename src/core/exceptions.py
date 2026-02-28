from fastapi import HTTPException, status

def credentials_exception(reason: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail=reason) 

user_exists_exception: HTTPException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User already exists"
)

def bad_requset(reason: str = "Bad Request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=reason)

code_verification_exception: HTTPException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Wrong code"
)

email_not_in_the_system_exception: HTTPException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Email is not verified"
)

user_not_found: HTTPException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="User not found"
)

card_not_found: HTTPException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Card not found"
)

cannot_delete_card_with_balance: HTTPException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Cannot delete card with non-zero balance"
)

saving_account_not_found: HTTPException = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Saving account not found"
)

cannot_delete_saving_account_with_balance: HTTPException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Cannot delete saving account with non-zero balance"
)




def forbidden_wallet_action(reason: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                         detail=reason)