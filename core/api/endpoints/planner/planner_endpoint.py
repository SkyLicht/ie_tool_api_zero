from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.api.dependency import get_scoped_db_session, get_current_user
from core.api.request.planner_request import CreateWorkPlanRequest
from core.auth.security import check_permission
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.planner.work_day_repository import WorkDayRepository
from core.data.repositroy.planner.work_plan_repository import WorkPlanRepository

router = APIRouter(
    prefix="/planner",
    tags=["planner"],
)

def get_planner_repository(db: Session = Depends(get_scoped_db_session)):
    return WorkDayRepository(db)

def get_work_plan_repository(db: Session = Depends(get_scoped_db_session)):
    return WorkPlanRepository(db)


@router.get("/get_by_str_date")
async def get_or_create_by_str_date(
        str_date: str,
        repo: WorkDayRepository = Depends(get_planner_repository),
        user: UserModel = Depends(get_current_user)
):
    try:

        check_permission(user, ["*"], ['admin', 'edit'])

        return repo.get_or_create_by_str_date(str_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()

@router.post("/create_work_plan")
async def create_work_plan(
        body: CreateWorkPlanRequest,
        repo: WorkPlanRepository = Depends(get_work_plan_repository),
        user: UserModel = Depends(get_current_user)
):
    try:

        check_permission(user, ["*"], ['admin', 'edit'])
        return repo.create_work_plan(body.to_orm())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()


@router.get("/get_work_plans_by_str_date")
async def get_work_plans_by_str_date(
        str_date: str,
        repo: WorkPlanRepository = Depends(get_work_plan_repository),
        user: UserModel = Depends(get_current_user)
):
    try:

        check_permission(user, ["*"], ['admin', 'edit'])
        return repo.get_work_plans_by_str_date(str_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()

@router.get("/get_work_plan_by")
async def get_work_plan_by_work_day_id(
        work_day_id: str,
        str_date: str,
        repo: WorkPlanRepository = Depends(get_work_plan_repository),
        user: UserModel = Depends(get_current_user)
):
    try:

        check_permission(user, ["*"], ['admin', 'edit'])
        return repo.get_work_plan_by_work_day_and_date(work_day_id, str_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        repo.session.close()