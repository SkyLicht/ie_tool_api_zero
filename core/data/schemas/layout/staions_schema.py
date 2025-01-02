from pydantic import BaseModel


class StationSchema(BaseModel):
    id: str


class StationsReadSchema(BaseModel):
    stations: list[StationSchema]