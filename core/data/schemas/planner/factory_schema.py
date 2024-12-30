from pydantic import BaseModel

from core.data.schemas.planner.line_schema import LineSmallSchema

class FactoryWithLinesSchema(BaseModel):
    id: str
    name: str
    lines: list[LineSmallSchema]