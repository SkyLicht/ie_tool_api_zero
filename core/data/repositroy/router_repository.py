from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.data.dao.router_access_dao import RouterAccessDAO
from core.data.models.it_tool_orm_models import RouterAccessModel
from core.logger_manager import LoggerManager


class RouterAccessRepository:

    def __init__(self, db: Session):
        self.logger = LoggerManager.get_logger(name= 'api')
        self.dao = RouterAccessDAO(db, self.logger)


    def create_router_access(self, route_pattern: str, _type: str) -> RouterAccessModel:
        # Check if router access already exists
        existing_router_access = self.dao.get_router_access_by_pattern(route_pattern)

        if existing_router_access:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Router access already exists."
            )

        # Create router access
        router_access = self.dao.create(RouterAccessModel(route_pattern=route_pattern, type=_type))
        return router_access



