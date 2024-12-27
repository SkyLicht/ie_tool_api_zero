from typing import List

from pydantic import BaseModel

from core.data.schemas.role_schema import PermissionSchema


class RouteSchema(BaseModel):
    route_pattern: str

class RouteRoleSchema(BaseModel):
    type: str
    route_pattern: str
    role_name: str
    permissions: List[PermissionSchema]