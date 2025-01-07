from typing import List, Type

from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import CycleTimeTakeModel


class LineBalanceTakeDAO:

    def __init__(self, session: Session):
        self.session = session

    def create(self, take: CycleTimeTakeModel)-> str:
        try:
            self.session.add(take)
            self.session.commit()
            self.session.refresh(take)
            return take.id
        except Exception as e:
            self.session.rollback()
            raise e

    def get_by_line_balance_id(self, line_balance_id)-> List[Type[CycleTimeTakeModel]]:
        return self.session.query(CycleTimeTakeModel).filter_by(line_balance_id=line_balance_id).all()

    def delete_by_id(self, take_id):
        try:
            take = self.session.query(CycleTimeTakeModel).filter_by(id=take_id).first()
            if not take:
                raise Exception(f"Take with id {take_id} not found")
            else:
                self.session.delete(take)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

