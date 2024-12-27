from pydantic import BaseModel



class PermissionSchema(BaseModel):
    name: str

class RoleSchema(BaseModel):
    name: str
    permissions: list[PermissionSchema]