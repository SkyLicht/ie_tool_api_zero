from core.data.dao.planner.area_dao import AreaDAO
from core.data.dao.planner.layout_dao import LayoutDAO
from core.data.dao.planner.operation_dao import OperationDAO
from core.data.dao.planner.station_dao import StationDAO
from core.data.models.it_tool_orm_models import UserModel, StationModel
from core.logger_manager import LoggerManager


class LayoutRepository:
    def __init__(self, session, user: 'UserModel'):
        self.session = session
        self.logger = LoggerManager.get_logger(name="LayoutRepository", log_file_name="db", username=user.username)
        self.layout_dao = LayoutDAO(session, self.logger)
        self.user = user
        self.station_dao = StationDAO(session, self.logger)
        self.operation_dao = OperationDAO(session, self.logger)
        self.area_dao = AreaDAO(session, self.logger)

    def create_layout_by_line_id(self, line_id: str):
        return self.layout_dao.create_layout_by_line_id(line_id, self.user.id)

    def update_stations_in_layout(self, layout_id, stations):

        if len(stations) == 0:
            self.logger.error("No stations to update")
            return

        _stations = self.station_dao.get_stations_by_layout_id(layout_id)

        # If the list are equal, check for id and index, no need to  update
        if len(_stations) == len(stations):
            for i, station in enumerate(stations):
                if _stations[i].operation_id != station["operation_id"] or _stations[i].index != station["index"]:
                    break
            else:
                self.logger.info("No need to update stations")
                return

        if not _stations:
            # Create new stations
            for station in stations:
                self.station_dao.create_station(
                    StationModel(layout_id=layout_id, index=station['index'], operation_id=station["operation_id"],
                                 area_id=station["area_id"]))
            return

        # Update existing stations
        for station in stations:
            _station = next((x for x in _stations if x.operation_id == station["operation_id"]), None)
            if _station:
                _station.index = station["index"]
                _station.area_id = station["area_id"]
                self.station_dao.update_station(_station)
            else:
                self.station_dao.create_station(
                    StationModel(layout_id=layout_id, index=station['index'], operation_id=station["operation_id"],
                                 area_id=station["area_id"]))

        # Delete stations that are not in the new list
        for _station in _stations:
            if not any(x["operation_id"] == _station.operation_id for x in stations):
                self.station_dao.delete_station(_station.id)

        return

    def get_layout_by_id(self, layout_id):
        _layout = self.layout_dao.get_layout_by_id(layout_id)

        short_user = {
            "username": _layout.user.username
        }

        _layout.stations.sort(key=lambda x: x.index)

        _layout_dict = {
            "id": _layout.id,
            "is_active": _layout.is_active,
            "user": short_user,
            "stations": _layout.stations,
            "line_id": _layout.line_id,
            'line_name': _layout.line.name,
            'factory_id': _layout.line.factory.id,
            'factory': _layout.line.factory.name
        }

        if not _layout:
            self.logger.error(f"Layout not found: {layout_id}")
            return None

        self.logger.info(f"Layout found: {_layout.id}")

        return _layout_dict

    def get_all_layouts(self):
        _layouts = self.layout_dao.get_all_layouts()

        _refined_layouts = []

        for layout in _layouts:
            layout_dict = {
                "id": layout.id,
                "is_active": layout.is_active,
                "stations": layout.stations,
                "line_id": layout.line_id,
                'line_name': layout.line.name,
                'factory_id': layout.line.factory.id,
                'factory': layout.line.factory.name
            }

            _refined_layouts.append(layout_dict)

        _refined_layouts.sort(key=lambda x: x["line_name"])

        if len(_layouts) > 0:
            self.logger.info(f"Layouts found: {len(_layouts)}")
        else:
            self.logger.error(f"Layouts not found")

        return _refined_layouts

    def get_all_stations(self):
        _stations = self.station_dao.get_all_stations()
        if len(_stations) > 0:
            self.logger.info(f"Stations found: {len(_stations)}")
        else:
            self.logger.error(f"Stations not found")

        return _stations

    def get_all_operations(self):
        _operations = self.operation_dao.get_all_operations()
        if len(_operations) > 0:
            self.logger.info(f"Operations found: {len(_operations)}")
        else:
            self.logger.error(f"Operations not found")

        return _operations

    def get_all_operations_and_areas(self):
        _operations = self.operation_dao.get_all_operations()
        if len(_operations) > 0:
            self.logger.info(f"Operations found: {len(_operations)}")
        else:
            self.logger.error(f"Operations not found")

        _areas = self.area_dao.get_all_areas()

        if len(_areas) > 0:
            self.logger.info(f"Areas found: {len(_areas)}")
        else:
            self.logger.error(f"Areas not found")

        return {
            "operations": _operations,
            "areas": _areas
        }
