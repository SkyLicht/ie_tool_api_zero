from fastapi import APIRouter, Depends

from core.api.dependency import get_current_user
from core.data.models.it_tool_orm_models import UserModel

router = APIRouter(
    prefix="/test",
    tags=["test"],
)

@router.get("/")
async def read_users(user: UserModel = Depends(get_current_user)):

    return [{"username":"rick"}, {"username":"morty"}]