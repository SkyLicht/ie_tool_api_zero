from typing import List
from sqlalchemy.orm import Session

from core.data.dao.planner.workplan_dao import WorkPlanDAO
from core.data.schemas.planner_schema import WorkPlanSchema


class WorkPlanRepository:

    def __init__(self, session: Session):
        self.session = session
        self.work_plan_dao = WorkPlanDAO(session)


    def create_work_plan(self, work_plan):
        return self.work_plan_dao.create_work_plan(work_plan)

    def get_work_plans_by_str_date(self, str_date):
        return self.work_plan_dao.get_work_plans_by_str_date(str_date)

    def get_work_plan_by_work_day_and_date(self, work_day_id, str_date)-> 'List[WorkPlanSchema]':
        orm = self.work_plan_dao.get_work_plan_by_work_day_id_and_date(work_day_id, str_date)

        return [WorkPlanSchema.from_orm_to(orm) for orm in orm]