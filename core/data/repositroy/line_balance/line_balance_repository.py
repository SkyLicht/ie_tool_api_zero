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
    if record.station is None:
        return None

    return {
        "id": record.id,
        "station_id": record.station_id,
        "cycle_time": record.cycle_time,
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

        return [
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
                    "stations": [
                        {
                            "id": station.id,
                            "operation_id": station.operation_id,
                            "index": station.index,
                            "label": station.operation.label
                        } for station in line_balance.layout.stations
                    ]
                },
                "created_at": str(line_balance.created_at),
                "updated_at": str(line_balance.updated_at),
            } for line_balance in line_balances
        ]

    def get_line_balance_by_id(self, line_balance_id: str):
        orm = self.line_balance_dao.get_by_id(line_balance_id)

        if not orm:
            raise HTTPException(status_code=404, detail=f"Line balance {line_balance_id} not found")

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
            return {
                "id": take.id,
                "work_plan": serialize_work_plan(take.work_plan),
                "records": [serialize_record(record) for record in take.records],
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

        line_balance = {
            "id": orm.id,
            "str_date": orm.str_date,
            "week": orm.week,
            "layout": serialize_layout(orm.layout),
            "takes": [serialize_take(take) for take in orm.takes],
        }

        # print(json.dumps(line_balance.get('takes'), indent=4))

        return line_balance

    def delete_take(self, take_id):
        pass

    def create_take(self, line_balance_id):
        line = self.line_balance_dao.get_line_from_line_balance(line_balance_id)
        if not line:
            raise HTTPException(status_code=404, detail=f"Line balance {line_balance_id} not found")

        work_plan = self.work_plan_dao.get_work_plan_by_line_id(line.id)

        if not work_plan:
            raise HTTPException(status_code=404, detail=f"Work plans for line {line.name} not found")

        line_balance = self.take_dao.create(CycleTimeTakeModel(
            line_balance_id=line_balance_id,
            user_id=self.user.id,
            work_plan_id=work_plan.id
        ))
        return {
            "id": line_balance,
        }

    def get_takes_by_layout(self, layout_id) -> List[Dict]:
        orm_takes = self.take_dao.get_by_line_balance_id(layout_id)

        if not orm_takes:
            raise HTTPException(status_code=404, detail=f"Line balance takes for layout {layout_id} not found")

        return [
            {
                "id": take.id,
                "work_plan_id": take.work_plan_id,
                "user_id": take.user_id,
                'user_name': take.user.username,
                "created_at": str(take.created_at),
                "updated_at": str(take.updated_at),
            } for take in orm_takes
        ]

    def get_cycle_times_by_take_id(self, take_id):
        orm = self.cycle_time_dao.get_all_by_take_id(take_id)

        if not orm:
            return []

        return [serialize_record(record) for record in orm]
