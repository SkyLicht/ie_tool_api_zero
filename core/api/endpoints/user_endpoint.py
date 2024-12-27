from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.api.dependency import get_current_user, get_scoped_db_session
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.user_repository import UserRepository
from core.data.schemas.user_schema import UserTranslate
from core.logger_manager import LoggerManager

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

def get_user_repository(db: Session = Depends(get_scoped_db_session)):
    return UserRepository(db, LoggerManager.get_logger(name="api"))

@router.get("/")
async def get_user_by_token(
    user: UserModel = Depends(get_current_user)
):
    try:
        return UserTranslate.orm_to_user_auth_webapp(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




class AddRouterRequest(BaseModel):
    user_name: str
    route_pattern: str
    role_name: str

@router.post("/add_router")
async def add_router_to_user(
    body: AddRouterRequest,
    user: UserModel = Depends(get_current_user),
    repo: UserRepository = Depends(get_user_repository)
):
    try:
        repo.add_route_to_user(body.user_name, body.route_pattern, body.role_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
