from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.data.dao.planner.line_dao import LineDAO
from core.data.dao.planner.work_day_dao import WorkDayDAO
from core.data.models.it_tool_orm_models import UserModel
from core.logger_manager import LoggerManager


class WorkDayRepository:
    def __init__(self, session: Session, user: 'UserModel'):
        self.session = session
        self.logger = LoggerManager.get_logger(name="WorkDayRepository", log_file_name="db", username=user.username)
        self.line_dao = LineDAO(session, self.logger)
        self.work_day_dao = WorkDayDAO(session, self.logger)
        self.user = user

    def __enter__(self):
        # Perform setup actions, e.g., open a database connection
        print("Entering context and setting up resources.")
        return self  # Return the object to be used in the with block

    def __exit__(self, exc_type, exc_value, traceback):
        # Perform cleanup actions, e.g., close the database connection
        print("Exiting context and cleaning up resources.")
        # Handle exceptions if necessary; return True to suppress them, False to propagate
        return False

    def get_or_create_by_str_date(self, str_date: str):
        lines = self.line_dao.get_all()
        if not lines:
            raise HTTPException(status_code=404, detail="No lines found")

        for line in lines:
            self.work_day_dao.create(str_date, line.id)

        list_orm = self.work_day_dao.get_by_str_date(str_date)

        list_orm.sort(key=lambda x: x.line.name)

        return list_orm

    # def get_work_day(self, work_day_id: int) -> WorkDay:
    #     return self.db.query(WorkDay).filter(WorkDay.id == work_day_id).first()
    #
    # def get_work_days(self, user_id: int) -> List[WorkDay]:
    #     return self.db.query(WorkDay).filter(WorkDay.user_id == user_id).all()
    #
    # def create_work_day(self, work_day: WorkDay) -> WorkDay:
    #     self.db.add(work_day)
    #     self.db.commit()
    #     self.db.refresh(work_day)
    #     return work_day
    #
    # def update_work_day(self, work_day: WorkDay) -> WorkDay:
    #     self.db.commit()
    #     self.db.refresh(work_day)
    #     return work_day
    #
    # def delete_work_day(self, work_day_id: int) -> None:
    #     work_day = self.get_work_day(work_day_id)
    #     self.db.delete(work_day)
    #     self.db.commit()
