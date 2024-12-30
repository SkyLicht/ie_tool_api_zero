from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import StationModel


class StationDAO:
    def __init__(self, session: Session, logger):
        self.session = session
        self.logger = logger

    def get_all_stations(self):
        return self.session.query(StationModel).all()

    def get_stations_by_layout_id(self, layout_id):
        return (self.session.query(StationModel)
                .filter(StationModel.layout_id == layout_id)
                .all())

    def update_stations(self, stations):
        try:
            self.session.add_all(stations)
            self.session.commit()
            self.logger.info(f"Stations updated")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while updating stations: {e}")
            raise

    def create_station(self, station: StationModel):
        try:
            self.session.add(station)
            self.session.commit()
            self.session.refresh(station)
            self.logger.info(f"Station {station.operation.label} created")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while creating station: {e}")
            raise

    def delete_station(self, station_id):
        try:
            station = self.session.query(StationModel).get(station_id)
            self.session.delete(station)
            self.session.commit()
            self.logger.info(f"Station {station_id} deleted")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while deleting station: {e}")
            raise

    def update_station(self, station: StationModel):
        try:
            self.session.add(station)
            self.session.commit()
            self.logger.info(f"Station {station.operation.label} updated")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while updating station: {e}")
            raise