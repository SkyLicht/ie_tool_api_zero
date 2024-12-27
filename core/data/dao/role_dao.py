from typing import Type, Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.data.dao.permission_dao import PermissionDAO
from core.data.models.it_tool_orm_models import RoleModel



class RoleDAO:
    def __init__(self, db: Session, logger):
        self.db = db
        self.logger = logger

    def get_or_create_role(self, role_name: str) -> RoleModel:
        try:
            role = self.db.query(RoleModel).filter(RoleModel.name == role_name).first()
            if not role:
                role = RoleModel(name=role_name)
                self.db.add(role)
                self.db.commit()
                self.db.refresh(role)
                self.logger.info(f'Role "{role_name}" created')
            else:
                self.logger.info(f'Role "{role_name}" already exists')

            self.logger.info(f'Returning role: {role}')
            return role

        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while getting or creating role '{role_name}': {e}")
            raise

    def add_permission_to_role(self, role_name: str, permission_name: str) -> RoleModel:
        try:
            role = self.get_or_create_role(role_name)
            permission_dao = PermissionDAO(self.db, self.logger)
            permission = permission_dao.get_or_create_permission(permission_name)

            if permission not in role.permissions:
                role.permissions.append(permission)
                self.db.commit()
                self.db.refresh(role)
                self.logger.info(f'Permission "{permission_name}" added to role "{role_name}"')
            else:
                self.logger.info(f'Permission "{permission_name}" is already associated with role "{role_name}"')

            return role

        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while adding permission '{permission_name}' to role '{role_name}': {e}")
            raise

    def find_role_by_name(self, role_name: str) -> Optional[RoleModel]:
        try:
            role = self.db.query(RoleModel).filter(RoleModel.name == role_name).first()
            return role
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while finding role '{role_name}': {e}")
            raise

    def create_all(self, roles: List[RoleModel]):
        try:
            self.db.add_all(roles)
            self.db.commit()
            self.logger.info(f'Roles created')
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while creating roles: {e}")
            raise