from sqlalchemy.exc import SQLAlchemyError
from core.data.models.it_tool_orm_models import WorkDayModel
class WorkDayDAO:
    def __init__(self, db, logger):
        self.logger = logger
        self.db = db

    def get_or_create_by_str_date_line(self, str_date, line_id):
        try:
            # Query for the existing work day
            work_day = (self.db.query(WorkDayModel)
                        .filter(WorkDayModel.str_date == str_date)
                        .filter(WorkDayModel.line_id == line_id)
                        .first())
            if work_day is None:
                # Create a new work day if not found
                work_day = WorkDayModel(str_date=str_date, line_id=line_id, week=1)
                self.db.add(work_day)
                self.db.commit()
                self.db.refresh(work_day)  # Ensure the object is updated with database values

            return work_day
        except SQLAlchemyError as e:
            self.db.rollback()
            self.logger.error(f"Error while getting or creating work day '{str_date}': {e}")
            raise

    def get_work_day(self, work_day_id):
        return self.db.query(WorkDayModel).filter(WorkDayModel.id == work_day_id).first()

    def get_work_days(self, user_id, start_date, end_date):
        return self.db.query(WorkDayModel).filter(
            WorkDayModel.date >= start_date,
            WorkDayModel.date <= end_date,
        ).all()

    def create_work_day(self, user_id, date):
        work_day = WorkDayModel(date=date)
        self.db.add(work_day)
        self.db.commit()
        return work_day

    def update_work_day(self, work_day_id, **kwargs):
        work_day = self.get_work_day(work_day_id)
        for key, value in kwargs.items():
            setattr(work_day, key, value)
        self.db.commit()
        return work_day

    def delete_work_day(self, work_day_id):
        work_day = self.get_work_day(work_day_id)
        self.db.delete(work_day)
        self.db.commit()
        return work_day
