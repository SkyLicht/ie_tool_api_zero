from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from core.data.models.it_tool_orm_models import WorkDayModel, LineModel


class WorkDayDAO:
    def __init__(self, db, logger):
        self.logger = logger
        self.db = db

    def create(self, str_date, line_id):
        try:
            # Query for the existing work day
            work_day = (self.db.query(WorkDayModel)
                        .options(joinedload(WorkDayModel.line).joinedload(LineModel.factory))
                        .filter(WorkDayModel.str_date == str_date)
                        .filter(WorkDayModel.line_id == line_id)
                        .first())
            if work_day is None:
                # Create a new work day if not found
                work_day = WorkDayModel(str_date=str_date, line_id=line_id, week=1)
                self.db.add(work_day)
                self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while getting or creating work day '{str_date}': {e}")
            raise

    def get_by_str_date(self, str_date)-> List[WorkDayModel]:
        return (self.db.query(WorkDayModel)
                .options(joinedload(WorkDayModel.line).joinedload(LineModel.factory))
                .filter(WorkDayModel.str_date == str_date)
                .all())
