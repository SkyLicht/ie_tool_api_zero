from typing import List

from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import PermissionModel

from sqlalchemy.exc import SQLAlchemyError


class PermissionDAO:
    def __init__(self, db: Session, logger):
        self.db = db
        self.logger = logger

    def get_or_create_permission(self, permission_name: str) -> PermissionModel:
        try:
            permission = self.db.query(PermissionModel).filter(PermissionModel.name == permission_name).first()
            if not permission:
                permission = PermissionModel(name=permission_name)
                self.db.add(permission)
                self.db.commit()
                self.db.refresh(permission)
                self.logger.info(f'Permission "{permission_name}" created')
            else:
                self.logger.info(f'Permission "{permission_name}" already exists')

            self.logger.info(f'Returning permission: {permission}')
            return permission

        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while getting or creating permission '{permission_name}': {e}")
            raise

    def create(self, permission: PermissionModel):
        try:
            self.db.add(permission)
            self.db.commit()
            self.db.refresh(permission)
            self.logger.info(f'Permission "{permission.name}" created')
            return permission
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while creating permission '{permission.name}': {e}")
            raise

    def create_all(self, permissions: List[PermissionModel]):
        try:
            self.db.add_all(permissions)
            self.db.commit()
            self.logger.info(f'Permissions created')
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while creating permissions: {e}")
            raise
