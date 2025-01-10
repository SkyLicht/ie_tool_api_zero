from typing import List

from pydantic import BaseModel

from core.data.models.it_tool_orm_models import UserModel
from core.data.schemas.role_schema import PermissionSchema
from core.data.schemas.route_schema import RouteRoleSchema


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role_name: str


class UserOut(UserBase):
    id: str
    role_name: str


class UserAuth(BaseModel):
    user_id: str
    username: str
    routes: List[RouteRoleSchema]

    def has_permission(self, routes: List[str], permissions: List[str]) -> dict:
        respond = {
            'has_route_access': True,
            "has_permission": True,
            "message": "User does not have the required permission"
        }
        # Check if the user has at least one of the required routes.
        # for route_record in routes:
        #     for user_route in self.routes:
        #         if user_route.route_pattern == route_record:
        #             respond['has_route_access'] = True
        #             # Check if the user has at least one of the required permissions.
        #             for permission_record in permissions:
        #                 for user_permission in user_route.permissions:
        #                     if user_permission.name == permission_record:
        #                         respond['has_permission'] = True
        #                         respond['message'] = "User has the required permission"
        #                         return respond


        return respond


class UserTranslate(BaseModel):
    @staticmethod
    def orm_to_user_auth(orm: UserModel) -> UserAuth:
        routes: List[RouteRoleSchema] = []
        for records in orm.user_route_roles:
            routes.append(RouteRoleSchema(
                type=records.route.type,
                route_pattern=records.route.route_pattern,
                role_name=records.role.name,
                permissions=[PermissionSchema(name=permission.name) for permission in records.role.permissions]
            ))
        return UserAuth(
            user_id=orm.id,
            username=orm.username,
            routes=routes
        )

    @staticmethod
    def orm_to_user_auth_webapp(orm: UserModel) -> UserAuth:
        routes: List[RouteRoleSchema] = []
        for records in orm.user_route_roles:
            if records.route.type != "webapp": continue
            routes.append(RouteRoleSchema(
                type=records.route.type,
                route_pattern=records.route.route_pattern,
                role_name=records.role.name,
                permissions=[PermissionSchema(name=permission.name) for permission in records.role.permissions]
            ))
        return UserAuth(
            user_id=orm.id,
            username=orm.username,
            routes=routes
        )
