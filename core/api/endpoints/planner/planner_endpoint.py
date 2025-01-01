from fastapi import APIRouter, Depends, HTTPException

from core.api.dependency import get_planner_repository, get_work_plan_repository
from core.api.request.planner_request import CreateWorkPlanRequest
from core.auth.security import check_permission
from core.data.repositroy.planner.work_day_repository import WorkDayRepository
from core.data.repositroy.planner.work_plan_repository import WorkPlanRepository
from core.logger_manager import LoggerManager

router = APIRouter(
    prefix="/planner",
    tags=["planner"],
)
logger = LoggerManager.get_logger(name="PlannerEndpoint", log_file_name="api", username="SYSTEM")


@router.get("/get_by_str_date")
async def get_or_create_by_str_date(
        str_date: str,
        repo: WorkDayRepository = Depends(get_planner_repository),
):
    try:
        check_permission(repo.user, ["*"], ['admin', 'edit'])
        return repo.get_or_create_by_str_date(str_date)
    except PermissionError as e:
        logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    finally:
        pass


@router.post("/create_work_plan")
async def create_work_plan(
        body: CreateWorkPlanRequest,
        repo: WorkPlanRepository = Depends(get_work_plan_repository),
):
    try:
        check_permission(repo.user, ["*"], ['admin', 'edit'])
        return repo.create_work_plan(body.to_orm())
    except PermissionError as e:
        logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    finally:
        pass


# @router.get("/get_work_plans_by_str_date")
# async def get_work_plans_by_str_date(
#         str_date: str,
#         repo: WorkPlanRepository = Depends(get_work_plan_repository),
# ):
#     try:
#         check_permission(repo.user, ["*"], ['admin', 'edit'])
#         return repo.get_work_plans_by_str_date(str_date)
#     except PermissionError as e:
#         logger.error(f"Permission Error: {str(e)}")
#         raise HTTPException(status_code=403, detail="Permission denied.")
#     except ValueError as e:
#         logger.error(f"Invalid Input: {str(e)}")
#         raise HTTPException(status_code=422, detail=str(e))
#     except Exception as e:
#         logger.error(f"Unexpected Error: {str(e)}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred.")
#     finally:
#         pass

# todo: Raname this endpoint to get_work_plan_by_work_day_id_and_date
@router.get("/get_work_plan_by")
async def get_work_plan_by_work_day_id(
        work_day_id: str,
        repo: WorkPlanRepository = Depends(get_work_plan_repository),
):
    try:
        check_permission(repo.user, ["*"], ['admin', 'edit'])
        return repo.get_work_plans_by_id(work_day_id)
    except PermissionError as e:
        logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    finally:
        pass


#
# class WorkDayIDRequest(BaseModel):
#     work_day_id: str = Field(..., regex="^[a-f0-9]{24}$")  # Example for MongoDB ObjectId