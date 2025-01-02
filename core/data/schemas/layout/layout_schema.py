from pydantic import BaseModel


class StationNameSchema(BaseModel):
    id: str
    index: int
    label: str


class LayoutSchema(BaseModel):
    id: str
    line_id: str
    factory_id: str

    line_name: str
    factory_name: str

    is_active: bool
    version: str

    updated_at: str
    created_at: str

    stations: list[StationNameSchema]

    @staticmethod
    def from_layout_orm(orm):
        return LayoutSchema(
            id=orm.id,
            line_id=orm.line_id,
            factory_id=orm.line.factory_id,
            line_name=orm.line.name,
            factory_name=orm.line.factory.name,
            is_active=orm.is_active,
            version=str(orm.version),
            updated_at=str(orm.updated_at),
            created_at=str(orm.created_at),
            stations=[StationNameSchema(id=station.id, index=station.index, label=station.operation.label) for station
                      in orm.stations]
        )
