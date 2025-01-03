from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from core.api.dependency import get_line_balance_repository
from core.data.repositroy.line_balance.line_balance_repository import LineBalanceRepository

router = APIRouter(
    prefix="/line_balance",
    tags=["line_balance"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create")
async def create_line_balance(
    str_date: str,
    line_id: str,
    repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    try:
        return repo.create_line_balance(str_date, line_id)

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except PermissionError as e:
        repo.logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        repo.logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except SQLAlchemyError as e:
        repo.logger.error(f"SQLAlchemy Error: {str(e)}")
        raise HTTPException(status_code=400, detail= str(e))
    except Exception as e:
        repo.logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.get("/get_by_id")
async def get_line_balance_by_id(
    line_balance_id: str,
    repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    try:
        return repo.get_line_balance_by_id(line_balance_id)

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except PermissionError as e:
        repo.logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        repo.logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except SQLAlchemyError as e:
        repo.logger.error(f"SQLAlchemy Error: {str(e)}")
        raise HTTPException(status_code=400, detail= str(e))
    except Exception as e:
        repo.logger.error(f"Unexpected Error: {str(e)}")
        print(e)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. {str(e)}")


@router.get("/get_all_by_week")
async def get_all_line_balances_by_week(
    str_date: str,
    repo: LineBalanceRepository = Depends(get_line_balance_repository)
):
    try:
        return repo.get_all_line_balances_by_week(str_date)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        repo.logger.error(f"Permission Error: {str(e)}")
        raise HTTPException(status_code=403, detail="Permission denied.")
    except ValueError as e:
        repo.logger.error(f"Invalid Input: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except SQLAlchemyError as e:
        repo.logger.error(f"SQLAlchemy Error: {str(e)}")
        raise HTTPException(status_code=400, detail= str(e))
    except Exception as e:
        repo.logger.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")