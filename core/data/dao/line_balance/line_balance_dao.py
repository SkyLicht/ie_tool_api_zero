from typing import Tuple, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from core.data.models.it_tool_orm_models import LineBalanceModel, StationModel, LayoutModel, LineModel, \
    CycleTimeTakeModel, CycleTimeRecordModel, AreaModel


class LineBalanceDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create_line_balance(self, str_date: str, week: int, user_id: str, layout_id: str) -> Tuple[
        bool, LineBalanceModel]:
        try:
            is_existing = False
            line_balance = self.session.query(LineBalanceModel).filter_by(week=week, layout_id=layout_id).first()
            if not line_balance:
                line_balance = LineBalanceModel(str_date=str_date, week=week, user_id=user_id, layout_id=layout_id)
                self.session.add(line_balance)
                self.session.commit()
                self.session.refresh(line_balance)
            else:
                is_existing = True
            return is_existing, line_balance


        except SQLAlchemyError as e:
            self.session.rollback()
            raise

    def create(self, line_balance: LineBalanceModel):
        try:
            self.session.add(line_balance)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e

    def get_by_id(self, line_balance_id: str) -> Optional[LineBalanceModel]:
        try:
            return self.session.query(LineBalanceModel).options(
                joinedload(LineBalanceModel.layout),
                joinedload(LineBalanceModel.layout).joinedload(LayoutModel.stations),
                joinedload(LineBalanceModel.layout).joinedload(LayoutModel.stations).joinedload(StationModel.operation),
                joinedload(LineBalanceModel.layout).joinedload(LayoutModel.line),
                joinedload(LineBalanceModel.layout).joinedload(LayoutModel.line).joinedload(LineModel.factory),
                joinedload(LineBalanceModel.takes),
                joinedload(LineBalanceModel.takes).joinedload(CycleTimeTakeModel.records),
                joinedload(LineBalanceModel.takes).joinedload(CycleTimeTakeModel.records).joinedload(CycleTimeRecordModel.station),
                joinedload(LineBalanceModel.takes).joinedload(CycleTimeTakeModel.records).joinedload(CycleTimeRecordModel.station).joinedload(StationModel.area),
                joinedload(LineBalanceModel.user),
            ).filter_by(id=line_balance_id).first()
        except SQLAlchemyError as e:
            raise e


    def is_line_balance_exists(self, line_balance_id: str) -> bool:
        try:
            return self.session.query(LineBalanceModel).filter_by(id=line_balance_id).first() is not None
        except SQLAlchemyError as e:
            raise e

    def get_line_from_line_balance(self, line_balance_id: str)-> LineModel:
        try:
            return self.session.query(LineBalanceModel).filter_by(id=line_balance_id).first().layout.line
        except SQLAlchemyError as e:
            raise e

    def get_all(self):
        pass

    def get_all_by_week(self, week):
        try:
            return self.session.query(LineBalanceModel).filter_by(week=week).all()
        except SQLAlchemyError as e:
            raise e

    def delete_by_id(self, line_balance_id):
        try:
            # Fetch the LineBalanceModel instance
            line_balance = self.session.query(LineBalanceModel).filter_by(id=line_balance_id).first()
            if line_balance:
                self.session.delete(line_balance)  # This triggers cascading delete
                self.session.commit()
            else:
                raise ValueError(f"LineBalance with ID {line_balance_id} not found")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise e
