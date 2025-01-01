from fastapi import HTTPException

from core.auth.auth_utils import generate_custom_id
from core.data.dao.line_balance.line_balance_cycle_time_dao import LineBalanceCycleTimeDAO
from core.data.dao.line_balance.line_balance_dao import LineBalanceDAO
from core.data.dao.line_balance.line_balance_take_dao import LineBalanceTakeDAO
from core.data.dao.planner.layout_dao import LayoutDAO
from core.data.dao.planner.work_plan_dao import WorkPlanDAO
from core.data.models.it_tool_orm_models import UserModel, CycleTimeTakeModel, LineBalanceModel, CycleTimeRecordModel
from core.logger_manager import LoggerManager
from core.utils.date_utils import get_iso_week_number


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




        is_existing , line_balance = self.line_balance_dao.get_or_create_line_balance(
            str_date=str_date,
            week=week,
            user_id=self.user.id,
            layout_id=layout.id
        )

        if is_existing :
            raise HTTPException(status_code=400, detail="Line balance already exists")

        line_balance_take = CycleTimeTakeModel(
            id= generate_custom_id(),
            platform_id= work_plan.platform_id,
            line_balance_id= line_balance.id,
            user_id= self.user.id,
        )

        cycle_times = [CycleTimeRecordModel(
            id = generate_custom_id(),
            cycle_time = [0],
            user_id= self.user.id,
            take_id= line_balance_take.id,
            station_id= station.id,
        ) for station in layout.stations]



        self.take_dao.create(line_balance_take)
        self.cycle_time_dao.create_all(cycle_times)

        return line_balance.id


    def get_line_balance_by_id(self, line_balance_id: str):
        orm = self.line_balance_dao.get_by_id(line_balance_id)
        print(orm.takes)
        for take in orm.takes:
            print(take.records)
        return orm