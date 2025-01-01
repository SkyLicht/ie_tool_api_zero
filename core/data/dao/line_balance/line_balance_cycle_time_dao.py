from typing import List

from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import CycleTimeRecordModel


class LineBalanceCycleTimeDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(self, cycle_time: CycleTimeRecordModel):
        try:
            self.session.add(cycle_time)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


    def create_all(self, cycle_times: List[CycleTimeRecordModel]):
        try:
            self.session.add_all(cycle_times)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e