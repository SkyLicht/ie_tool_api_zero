from sqlalchemy.orm import Session

from core.data.models.it_tool_orm_models import AreaModel


class AreaDAO:
    def __init__(self, session: Session, logger):
        self.session = session
        self.logger = logger

    def get_all_areas(self):
        return self.session.query(AreaModel).all()