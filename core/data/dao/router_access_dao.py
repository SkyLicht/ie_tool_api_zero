from typing import Type, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import RouterAccessModel


class RouterAccessDAO:
    def __init__(self, db: Session, logger):
        self.db = db
        self.logger = logger

    def get_or_create_router_access(self, route_pattern: str) -> RouterAccessModel:
        try:
            router_access = self.db.query(RouterAccessModel).filter(RouterAccessModel.route_pattern == route_pattern).first()
            if not router_access:
                router_access = RouterAccessModel(route_pattern=route_pattern)
                self.db.add(router_access)
                self.db.commit()
                self.db.refresh(router_access)
                self.logger.info(f'Router access "{route_pattern}" created')
            else:
                self.logger.info(f'Router access "{route_pattern}" already exists')

            self.logger.info(f'Returning router access: {router_access}')
            return router_access

        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while getting or creating router access '{route_pattern}': {e}")
            raise


    def get_router_access_by_pattern(self, route_pattern: str) -> Optional[RouterAccessModel]:
        try:
            router_access = self.db.query(RouterAccessModel).filter(RouterAccessModel.route_pattern == route_pattern).first()
            return router_access
        except SQLAlchemyError as e:
            self.logger.error(f"Error while getting router access '{route_pattern}': {e}")
            raise

    def if_router_access_exists(self, route_pattern: str) -> bool:
        try:
            router_access = self.db.query(RouterAccessModel).filter(RouterAccessModel.route_pattern == route_pattern).first()
            return router_access is not None
        except SQLAlchemyError as e:
            self.logger.error(f"Error while checking if router access exists '{route_pattern}': {e}")
            raise

    def create(self, obj: RouterAccessModel):
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            self.logger.info(f'Router access "{obj.route_pattern}" created')
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while creating router access '{obj.route_pattern}': {e}")
            raise

