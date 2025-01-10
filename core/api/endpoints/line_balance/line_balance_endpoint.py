import functools

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.api.dependency import get_line_balance_repository
from core.auth.security import check_permission
from core.data.repositroy.line_balance.line_balance_repository import LineBalanceRepository

router = APIRouter(
    prefix="/line_balance",
    tags=["line_balance"],
    responses={404: {"description": "Not found"}},
)


# fast decorator to handle exceptions
# def route_exception_handler(func):
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         try:
#             return await func(*args, **kwargs)
#         except PermissionError as e:
#             raise HTTPException(status_code=403, detail="Permission denied.")
#         except ValueError as e:
#             raise HTTPException(status_code=422, detail=str(e))
#         except SQLAlchemyError as e:
#             raise HTTPException(status_code=400, detail=str(e))
#         except Exception as e:
#             raise HTTPException(status_code=500, detail="An unexpected error occurred.")
#
#     return wrapper


@router.post("/create")
async def create_line_balance(
        str_date: str,
        line_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.create_line_balance(str_date, line_id)

@router.get("/get_by_id")
async def get_line_balance_by_id(
        line_balance_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_line_balance_by_id(line_balance_id)


@router.get("/get_all_by_week")
async def get_all_line_balances_by_week(
        str_date: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_all_line_balances_by_week(str_date)

@router.get("/get_line_balances_by_week")
async def get_all_line_balances_by_week(
        week: int,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_line_balances_by_week(week)

class CreateTakeBody(BaseModel):
    line_balance_id: str
    stations_id: list[str]
@router.post("/create_task")
async def create_take(
        body: CreateTakeBody,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.create_take(body.line_balance_id, body.stations_id)


@router.get('/get_takes_by_line_balance')
async def get_take_by_id(
        line_balance: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_takes_by_layout(line_balance)

@router.get('/get_cycle_times_by_take_id')
async def get_cycle_times_by_take_id(
        take_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_cycle_times_by_take_id(take_id)

@router.delete('/delete_line_balance')
async def delete_line_balance(
        line_balance_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    repo.delete_line_balance(line_balance_id)
    return {
        "message": "Line balance deleted"
    }

@router.delete('/delete_take')
async def delete_take(
        take_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    repo.delete_take(take_id)
    return {
        "message": "Take deleted"
    }

@router.get('/get_stations_by_line_balance')
async def get_stations_by_line_balance(
        line_balance_id: str,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    return repo.get_stations_by_line_balance(line_balance_id)

class UpdateTakeBody(BaseModel):
    record_id: str
    cycles: list[int]
@router.patch('/update_record_by_id')
async def update_take(
        body: UpdateTakeBody,
        repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    check_permission(repo.user, ["*"], ['admin', 'edit'])
    repo.update_cycle_time(body.record_id, body.cycles)