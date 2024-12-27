from typing import List

from sqlalchemy.exc import SQLAlchemyError

from core.data.models.it_tool_orm_models import LineModel


class LineDAO:
    def __init__(self, session, logger):
        self.session = session
        self.logger = logger

    def create_line(self, line: LineModel):
        try:
            self.session.add(line)
            self.session.commit()
            self.logger.info(f"Line {line.name} created")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while creating line '{line.name}': {e}")
            raise

    def create_all(self, lines: List[LineModel]):
        try:
            self.session.add_all(lines)
            self.session.commit()
            self.logger.info(f"Lines created")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while creating lines: {e}")
            raise

    def create_one_by_one(self, lines: List[LineModel]):
        for line in lines:
            try:
                self.session.add(line)
                self.session.commit()
                self.logger.info(f"Line {line.name} created")
            except SQLAlchemyError as e:
                self.session.rollback()
                self.logger.error(f"Error while creating line '{line.name}': {e}")
                raise

    def get_all(self)-> List[LineModel]:
        return self.session.query(LineModel).all()