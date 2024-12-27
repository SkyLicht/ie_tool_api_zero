from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from core.data.dao.planner.line_dao import LineDAO
from core.data.dao.planner.work_day_dao import WorkDayDAO
from core.data.models.it_tool_orm_models import WorkDayModel
from core.logger_manager import LoggerManager


class WorkDayRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = LoggerManager.get_logger(name="WorkDayRepository", log_file_name="db", username="SYSTEM")
        self.line_dao = LineDAO(db, self.logger)
        self.work_day_dao = WorkDayDAO(db, self.logger)


    def get_or_create_by_str_date(self, str_date: str):
        lines = self.line_dao.get_all()
        if not lines:
            raise HTTPException(status_code=404, detail="No lines found")

        work_days: List[WorkDayModel] = [
            self.work_day_dao.get_or_create_by_str_date_line(str_date, line.id)
            for line in lines
        ]

        for work_day in work_days:
            print(work_day)

        return work_days


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