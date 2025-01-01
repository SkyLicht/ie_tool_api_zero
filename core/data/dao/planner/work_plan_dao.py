from typing import List

from sqlalchemy.orm import joinedload

from core.data.models.it_tool_orm_models import WorkPlanModel, LineModel


class WorkPlanDAO:
    def __init__(self, db):
        self.db = db

    def create_work_plan(self, work_plan: WorkPlanModel):
        try:
            self.db.add(work_plan)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    # todo: Remove this method
    def get_work_plans_by_str_date(self, str_date) -> List[WorkPlanModel]:
        return (self.db.query(WorkPlanModel)
                .options(
            joinedload(WorkPlanModel.platform),
            joinedload(WorkPlanModel.line),
            joinedload(WorkPlanModel.line).joinedload(LineModel.factory)
        )
                .filter(WorkPlanModel.str_date == str_date).all())

    def get_work_plan_by_id(self, work_day_id: str) -> List[WorkPlanModel]:
        return (self.db.query(WorkPlanModel)
                .options(
            joinedload(WorkPlanModel.platform),
            joinedload(WorkPlanModel.line),
            joinedload(WorkPlanModel.line).joinedload(LineModel.factory)
        )
                .filter(WorkPlanModel.work_day_id == work_day_id).all())

    def get_work_plan_by_line_id_and_str_date(self, line_id: str, str_date: str) -> WorkPlanModel:
        return (self.db.query(WorkPlanModel)
                .options(
            joinedload(WorkPlanModel.platform),
            joinedload(WorkPlanModel.line),
            joinedload(WorkPlanModel.line).joinedload(LineModel.factory)
        )
                .filter(WorkPlanModel.line_id == line_id, WorkPlanModel.str_date == str_date).first())
