from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import CycleTimeTakeModel


class LineBalanceTakeDAO:

    def __init__(self, session: Session):
        self.session = session

    def create(self, take: CycleTimeTakeModel):
        try:
            self.session.add(take)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


