from pydantic import BaseModel

from core.data.schemas.layout.layout_schema import LayoutSchema


class LineManagerSchema(BaseModel):
    id: str
    str_date: str
    week: int
    layout: LayoutSchema


    user_id: str
    user_name: str


