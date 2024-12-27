from typing import Optional, List, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.auth.auth_utils import get_password_hash
from core.data.dao.role_dao import RoleDAO
from core.data.dao.router_access_dao import RouterAccessDAO
from core.data.dao.user_dao import UserDAO
from core.data.models.it_tool_orm_models import UserModel
from core.data.schemas.user_schema import UserCreate


class UserRepository:
    def __init__(self, db: Session, logger):
        self.user_dao = UserDAO(db, logger)
        self.role_dao = RoleDAO(db, logger)
        self.route_dao = RouterAccessDAO(db, logger)
        self.logger = logger

    def create_user(self, user_data: UserCreate):
        # Check if user exists
        existing_user = self.user_dao.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken."
            )
        # Create or get role
        role = self.role_dao.get_or_create_role(user_data.role_name)
        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        user = self.user_dao.create_user(
            username=user_data.username,
            hashed_password=hashed_password,
            role_id=role.id,
        )
        return user

    def add_route_to_user(self, username: str, route_pattern: str, role_name: str) :
        user = self.user_dao.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # if route does not exist
        route = self.route_dao.get_router_access_by_pattern(route_pattern)
        if not route:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )

        # if role does not exist
        role = self.role_dao.find_role_by_name(role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )


        route = self.user_dao.add_user_route_role(
            user_id=user.id,
            route_id=route.id,
            role_id=role.id
        )
        #return route

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        user = self.user_dao.get_user_by_username(username)
        self.logger.info(f"User found: {user.to_dict()}")
        return user

    def get_all_users(self) -> List[Type[UserModel]]:
        return self.user_dao.get_all_users()
