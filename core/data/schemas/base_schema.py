from pydantic import BaseModel
from typing import TYPE_CHECKING, Type

# if TYPE_CHECKING:
#     from core.data.schemas.planner.factory_schema import FactorySchema

class FactorySchema(BaseModel):
    id: str
    name: str

class LineSchema(BaseModel):
    id: str
    is_active: bool
    created_at: str
    description: str
    name: str
    factory_id: str
    updated_at: str

    factory: FactorySchema


