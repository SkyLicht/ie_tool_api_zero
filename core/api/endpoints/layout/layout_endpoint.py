from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.api.dependency import get_scoped_db_session, get_current_user
from core.auth.security import check_permission
from core.data.models.it_tool_orm_models import UserModel
from core.data.repositroy.layout.layout_endpoint import LayoutRepository
from core.data.repositroy.planner.line_repository import LineRepository

router = APIRouter(
    prefix="/layout",
    tags=["layout"],
    responses={404: {"description": "Not found"}},
)


def get_line_repository(
        db: Session = Depends(get_scoped_db_session),
        user: UserModel = Depends(get_current_user)
):
    return LineRepository(db, user)


def get_layout_repository(
        db: Session = Depends(get_scoped_db_session),
        user: UserModel = Depends(get_current_user)
):
    return LayoutRepository(db, user)


@router.get("/get_lines")
async def get_lines(
        line_repo: LineRepository = Depends(get_line_repository),
):
    try:
        check_permission(line_repo.user, ["*"], ['admin', 'read'])
        return line_repo.get_factories_lines()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/create_layout")
async def create_layout(
        line_id: str,
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'edit'])
        return layout_repo.create_layout_by_line_id(line_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_layout_by_id")
async def get_layouts(
        layout_id: str,
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'read'])
        return layout_repo.get_layout_by_id(layout_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_layouts")
async def get_layouts(
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'read'])
        return layout_repo.get_all_layouts()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/get_stations")
async def get_stations(
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'read'])
        return layout_repo.get_all_stations()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/get_operations_areas")
async def get_operations(
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'read'])
        return layout_repo.get_all_operations_and_areas()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))





class LayoutBody(BaseModel):
    layout_id: str
    stations: list[dict]

@router.patch("/update_layout")
async def update_layout(
        body: LayoutBody,
        layout_repo: LayoutRepository = Depends(get_layout_repository),
):
    try:
        check_permission(layout_repo.user, ["*"], ['admin', 'edit'])
        return layout_repo.update_stations_in_layout(body.layout_id, body.stations)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

