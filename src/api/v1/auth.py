from http import HTTPStatus
from fastapi import Depends, APIRouter

from schemas.entity import UserInDB
from services.auth import AuthService, get_auth_service


router = APIRouter()


@router.post(
    path='/login',
    response_model=UserInDB,
    status_code=HTTPStatus.OK
)
async def login(
    auth_service: AuthService = Depends(get_auth_service)
):
    pass
