from typing import Optional, List, Type

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import UserModel, UserRouteRoleModel


class UserDAO:
    def __init__(self, db: Session, logger):
        self.db = db
        self.logger = logger

    def create_user(self, username: str, hashed_password: str, role_id: str) -> UserModel:
        try:
            user = UserModel(
                username=username,
                hashed_password=hashed_password,

            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            self.logger.info(f'User "{username}" created')
            return user
        except SQLAlchemyError as e:
            self.logger.error(f"Error while creating user '{username}': {e}")
            self.db.rollback()
            raise

    def add_user_route_role(self, user_id: str, route_id: str, role_id: str):
        try:
            self.db.add(UserRouteRoleModel(
                user_id=user_id,
                route_id=route_id,
                role_id=role_id
            ))
            self.db.commit()

            # return user_route_role
            self.logger.info(f"Route '{route_id}' added to user '{user_id}' with role '{role_id}'")

            # Insert record into association table
            # self.db.execute(api_user_route_role.insert().values(
            #     user_id=user.id,
            #     route_id=route.id,
            #     role_id=role.id
            # ))
            # self.db.commit()
            #
            # self.logger.info(f"Route '{route_pattern}' added to user '{username}' with role '{role_name}'")

        except SQLAlchemyError as e:
            self.logger.error(f"Error while adding route '{route_id}' to user '{user_id}' with role '{role_id}': {e}")
            self.db.rollback()
            raise

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_all_users(self) -> List[Type[UserModel]]:
        return self.db.query(UserModel).all()
