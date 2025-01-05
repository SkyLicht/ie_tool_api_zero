from typing import List, Type

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import CycleTimeRecordModel


class LineBalanceCycleTimeDAO:
    def __init__(self, session: Session):
        self.session = session

    def create(self, cycle_time: CycleTimeRecordModel):
        try:
            self.session.add(cycle_time)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e


    def create_all(self, cycle_times: List[CycleTimeRecordModel]):
        try:
            self.session.add_all(cycle_times)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_all_by_take_id(self, take_id: str)-> List[Type[CycleTimeRecordModel]]:
        try:
            return self.session.query(CycleTimeRecordModel).filter_by(take_id = take_id).all()
        except SQLAlchemyError as e:
            raise e