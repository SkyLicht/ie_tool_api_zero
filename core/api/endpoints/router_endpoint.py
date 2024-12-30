from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.api.dependency import get_scoped_db_session, get_current_user
from core.auth.security import check_permission
from core.data.models.it_tool_orm_models import RouterAccessModel, UserModel
from core.data.repositroy.router_repository import RouterAccessRepository

router = APIRouter(
    prefix="/router",
    tags=["router"],
)


def get_router_repository(db: Session = Depends(get_scoped_db_session)):
    return RouterAccessRepository(db)


class RouterAccessCreateRequest(BaseModel):
    type: str
    route_pattern: str




@router.post("/create")
async def create_router(
        body: RouterAccessCreateRequest,
        repo: RouterAccessRepository = Depends(get_router_repository),
        user: UserModel = Depends(get_current_user)
):
    try:

        check_permission(user, ["*", "router"], ['admin', 'edit'])
        repo.create_router_access(body.route_pattern, body.type)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()
