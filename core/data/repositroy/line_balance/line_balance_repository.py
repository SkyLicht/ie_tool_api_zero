import json
from typing import List, Dict

from fastapi import HTTPException

from core.auth.auth_utils import generate_custom_id
from core.data.dao.line_balance.line_balance_cycle_time_dao import LineBalanceCycleTimeDAO
from core.data.dao.line_balance.line_balance_dao import LineBalanceDAO
from core.data.dao.line_balance.line_balance_take_dao import LineBalanceTakeDAO
from core.data.dao.planner.layout_dao import LayoutDAO
from core.data.dao.planner.work_plan_dao import WorkPlanDAO
from core.data.models.it_tool_orm_models import UserModel, CycleTimeTakeModel, CycleTimeRecordModel
from core.logger_manager import LoggerManager
from core.utils.date_utils import get_iso_week_number
from core.utils.ie_utils import calculate_work_plan_residuals


def serialize_record(record):
    cycle_time = sum(record.cycle_time)
    _record = {
        "id": record.id,
        "station_id": record.station_id,
        "cycle_times": record.cycle_time,
        "ct": 0 if cycle_time == 0 else cycle_time / len(record.cycle_time),
        "index": record.station.index,
        "area": {
            "id": record.station.area.id,
            "index": record.station.area.index,
            "name": record.station.area.name,
            "section": record.station.area.section,
        },
        "station": {
            "id": record.station.id,
            "operation_id": record.station.operation.id,
            "operation_name": record.station.operation.label,
            "is_automatic": record.station.operation.is_automatic,
        }
    }

    return _record


def serialize_work_plan(work_plan):
    uph_target, commit, cycle_time = calculate_work_plan_residuals(
        target_oee=work_plan.target_oee,
        uph=work_plan.platform.uph,
        planned_hours=work_plan.planned_hours
    )
    return {
        "id": work_plan.id,
        "str_date": work_plan.str_date,
        "week": work_plan.week,
        "platform": {
            "id": work_plan.platform.id,
            "platform": work_plan.platform.platform,
            "uph": work_plan.platform.uph,
            "f_n": work_plan.platform.f_n,
            "components": work_plan.platform.components,
            "cost": work_plan.platform.cost,
            "height": work_plan.platform.height,
            "width": work_plan.platform.width,
            "sku": work_plan.platform.sku,
            "in_service": work_plan.platform.in_service,
        },
        "line": serialize_line(work_plan.line),
        "planned_hours": work_plan.planned_hours,
        "target_oee": work_plan.target_oee,
        "uph_custom": work_plan.uph_i,
        "uph_target": uph_target,
        "commit": commit,
        "cycle_time": cycle_time,
        "head_count": work_plan.head_count,
        "ft": work_plan.ft,
        "ict": work_plan.ict,
        "start_hour": work_plan.start_hour,
        "end_hour": work_plan.end_hour,
        "created_at": str(work_plan.created_at),
        "updated_at": str(work_plan.updated_at),
    }


def serialize_take(take):
    _records = [serialize_record(record) for record in take.records]
    _records.sort(key=lambda record: record["index"])
    return {
        "id": take.id,
        "work_plan": serialize_work_plan(take.work_plan),
        "records": _records,
        "created_at": str(take.created_at),
        "updated_at": str(take.updated_at),
    }


def serialize_layout(layout):
    return {
        "id": layout.id,
        "line_id": layout.line_id,
        "factory_id": layout.line.factory_id,
        "line_name": layout.line.name,
        "factory_name": layout.line.factory.name,
        "is_active": layout.is_active,
        "version": layout.version,
        "created_at": str(layout.created_at),
        "updated_at": str(layout.updated_at),
        # "stations": [
        #     {
        #         "id": station.id,
        #         "operation_id": station.operation_id,
        #         "index": station.index,
        #         "label": station.operation.label,
        #     } for station in layout.stations
        # ]
    }


def serialize_line(line):
    return {
        "id": line.id,
        "name": line.name,
        "factory": line.factory.name,
    }


def combine_takes(takes):
    if not takes: return []

    refactor_records = []

    # Gather all records from takes except the first one
    subsequent_records = [
        record for take in takes for record in take['records']
    ]

    # Function to find all cycle times (`ct`) for a given `station_id`
    def find_cycle_times(station_id):
        return [record['ct'] for record in subsequent_records if record['station_id'] == station_id]

    for record in takes[0]['records']:
        all_ct = find_cycle_times(record['station_id'])
        refactor_records.append(
            {
                "id": record['id'],
                "index": record['index'],
                "has_updated": True if len(all_ct) > 1 else False,
                "base_ct": record['ct'],
                "all_ct": all_ct,
                "last_ct": all_ct[-1],
                "station_id": record['station_id'],
                "area": record['area'],
                "station": record['station'],
            }
        )

    return refactor_records


class LineBalanceRepository:
    def __init__(self, session, user: UserModel):
        self.logger = LoggerManager.get_logger(name="LineBalanceRepository", log_file_name='db',
                                               username=user.username)
        self.session = session
        self.user = user
        self.layout_dao = LayoutDAO(session, self.logger)
        self.work_plan_dao = WorkPlanDAO(session)

        self.line_balance_dao = LineBalanceDAO(session)
        self.take_dao = LineBalanceTakeDAO(session)
        self.cycle_time_dao = LineBalanceCycleTimeDAO(session)

    def __enter__(self):
        # Perform setup actions, e.g., open a database connection
        # print("Entering context and setting up resources.")
        return self  # Return the object to be used in the with block

    def __exit__(self, exc_type, exc_value, traceback):
        # Perform cleanup actions, e.g., close the database connection
        # print("Exiting context and cleaning up resources.")
        # Handle exceptions if necessary; return True to suppress them, False to propagate
        return False

    def create_line_balance(self, str_date: str, line_id: str):
        week = get_iso_week_number(str_date)

        layout = self.layout_dao.get_layout_by_line_id(line_id)

        if not layout:
            raise HTTPException(status_code=404, detail=f"Layout for line {line_id} not found")

        work_plan = self.work_plan_dao.get_work_plan_by_line_id_and_str_date(line_id, str_date)

        if not work_plan:
            raise HTTPException(status_code=404, detail=f"Work plans for date {str_date} not found")

        is_existing, line_balance = self.line_balance_dao.get_or_create_line_balance(
            str_date=str_date,
            week=week,
            user_id=self.user.id,
            layout_id=layout.id
        )

        if is_existing:
            raise HTTPException(status_code=400, detail="Line balance already exists")

        line_balance_take = CycleTimeTakeModel(
            id=generate_custom_id(),
            work_plan_id=work_plan.id,
            line_balance_id=line_balance.id,
            user_id=self.user.id,
        )

        cycle_times = [CycleTimeRecordModel(
            id=generate_custom_id(),
            cycle_time=[0],
            user_id=self.user.id,
            take_id=line_balance_take.id,
            station_id=station.id,
        ) for station in layout.stations]

        self.take_dao.create(line_balance_take)
        self.cycle_time_dao.create_all(cycle_times)

        return line_balance.id

    def get_all_line_balances_by_week(self, str_date: str):
        week = get_iso_week_number(str_date)

        line_balances = self.line_balance_dao.get_all_by_week(week)



        _data =  [
            {
                "id": line_balance.id,
                "str_date": line_balance.str_date,
                "week": line_balance.week,
                "layout": {
                    "id": line_balance.layout.id,
                    "line_id": line_balance.layout.line_id,
                    "factory_id": line_balance.layout.line.factory_id,
                    "line_name": line_balance.layout.line.name,
                    "factory_name": line_balance.layout.line.factory.name,
                    "is_active": line_balance.layout.is_active,
                    "version": line_balance.layout.version,
                    "created_at": str(line_balance.layout.created_at),
                    "updated_at": str(line_balance.layout.updated_at),
                },
                "takes": [{"id": take.id} for take in line_balance.takes],

                "created_at": str(line_balance.created_at),
                "updated_at": str(line_balance.updated_at),
            } for line_balance in line_balances
        ]

        _data.sort(key=lambda item: item["line_name"])

        return _data

    def get_line_balances_by_week(self, week: int):
        line_balances = self.line_balance_dao.get_all_by_week(week)

        _data =  [
            {
                "id": line_balance.id,
                "str_date": line_balance.str_date,
                "week": line_balance.week,
                "layout": {
                    "id": line_balance.layout.id,
                    "line_id": line_balance.layout.line_id,
                    "factory_id": line_balance.layout.line.factory_id,
                    "line_name": line_balance.layout.line.name,
                    "factory_name": line_balance.layout.line.factory.name,
                    "is_active": line_balance.layout.is_active,
                    "version": line_balance.layout.version,
                    "created_at": str(line_balance.layout.created_at),
                    "updated_at": str(line_balance.layout.updated_at),
                },
                "takes": [{"id": take.id} for take in line_balance.takes],

                "created_at": str(line_balance.created_at),
                "updated_at": str(line_balance.updated_at),
            } for line_balance in line_balances
        ]

        _data.sort(key=lambda item: item["line_name"])

        return _data

    def get_line_balance_by_id(self, line_balance_id: str):
        _orm = self.line_balance_dao.get_by_id(line_balance_id)

        if not _orm:
            raise HTTPException(status_code=404, detail=f"Line balance {line_balance_id} not found")

        _orm.takes.sort(key=lambda x: x.created_at)
        takes = [serialize_take(take) for take in _orm.takes]
        refactor_cycles = combine_takes(takes)

        # print(json.dumps(refactor_cycles, indent=4))
        smt_bottleneck = max([item for item in refactor_cycles if item['area']['section'] == "SMT"],
                             key=lambda x: x['last_ct'])

        pth_bottleneck = max([item for item in refactor_cycles if item['area']['section'] == "PTH"],
                             key=lambda x: x['last_ct'])

        line_balance = {
            "id": _orm.id,
            "str_date": _orm.str_date,
            "week": _orm.week,
            "layout": serialize_layout(_orm.layout),
            "takes": takes,
            "refactored_records": refactor_cycles,
            "smt_bottleneck": smt_bottleneck,
            "packing_bottleneck": pth_bottleneck
        }

        # print(json.dumps(line_balance.get('takes'), indent=4))

        return line_balance

    def create_take(self, line_balance_id, stations_id: List[str]):
        line = self.line_balance_dao.get_line_from_line_balance(line_balance_id)
        if not line:
            raise HTTPException(status_code=404, detail=f"Line balance {line_balance_id} not found")

        work_plan = self.work_plan_dao.get_work_plan_by_line_id(line.id)

        if not work_plan:
            raise HTTPException(status_code=404, detail=f"Work plans for line {line.name} not found")

        line_balance = self.take_dao.create(CycleTimeTakeModel(
            line_balance_id=line_balance_id,
            user_id=self.user.id,
            work_plan_id=work_plan.id,
            records=[
                CycleTimeRecordModel(
                    cycle_time=[0],
                    user_id=self.user.id,
                    station_id=station_id,
                ) for station_id in stations_id
            ]
        ))
        return {
            "id": line_balance,
        }

    def get_takes_by_layout(self, layout_id) -> List[Dict]:
        _orm = self.take_dao.get_by_line_balance_id(layout_id)
        _orm.sort(key=lambda x: x.created_at)

        if not _orm:
            raise HTTPException(status_code=404, detail=f"Line balance takes for layout {layout_id} not found")

        _takes = [
            {
                "id": take.id,
                "work_plan_id": take.work_plan_id,
                "index": index,  # Adding index here
                "user_id": take.user_id,
                "user_name": take.user.username,
                "created_at": str(take.created_at),
                "updated_at": str(take.updated_at),
            }
            for index, take in enumerate(_orm, start=1)  # Start index from 1 (or 0 if needed)
        ]

        return _takes

    def get_cycle_times_by_take_id(self, take_id):
        orm = self.cycle_time_dao.get_all_by_take_id(take_id)

        if not orm:
            return []

        return [serialize_record(record) for record in orm].sort(key=lambda x: x['index'])

    def delete_line_balance(self, line_balance_id):
        self.line_balance_dao.delete_by_id(line_balance_id)

    def delete_take(self, take_id):
        self.take_dao.delete_by_id(take_id)

    def get_stations_by_line_balance(self, line_balance_id):
        _orm = self.line_balance_dao.get_by_id(line_balance_id)
        if not _orm:
            raise HTTPException(status_code=404, detail=f"Line balance {line_balance_id} not found")

        _stations = [
            {
                "id": station.id,
                "layout_id": station.layout_id,
                "index": station.index,
                "operation_id": station.operation_id,
                "operation_name": station.operation.label,
                "is_automatic": station.operation.is_automatic,
                "area_id": station.area_id,
                "area_name": station.area.name,
                "area_section": station.area.section,
            } for station in _orm.layout.stations
        ]

        _stations.sort(key=lambda x: x['index'])

        return _stations

    def update_cycle_time(self, record_id: str, cycles: list[int]):
        self.cycle_time_dao.update_by_id(record_id, cycles)
