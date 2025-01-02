from pydantic import BaseModel


class LineManagerTake(BaseModel):
    id: str
    platform_id: str
    updated_at: str
    created_at: str