from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.api.dependency import get_scoped_db_session, get_current_user
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.planner.platform_repository import PlatformRepository

router = APIRouter(
    prefix="/platform",
    tags=["platform"],
)


def get_planner_repository(db: Session = Depends(get_scoped_db_session)):
    return PlatformRepository(db)



@router.get("/get_all_in_service")
async def get_all_in_service(
        user: UserModel = Depends(get_current_user),
        repo: PlatformRepository = Depends(get_planner_repository)

):
    try:
        return repo.get_all_in_service()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()