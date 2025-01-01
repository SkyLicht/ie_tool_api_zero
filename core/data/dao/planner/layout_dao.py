from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from core.data.models.it_tool_orm_models import LayoutModel, LineModel


class LayoutDAO:

    def __init__(self, session, logger):
        self.session = session
        self.logger = logger

    def create_layout_by_line_id(self, line_id: str, user_id: str):
        layout = LayoutModel(line_id=line_id, user_id=user_id)
        try:
            self.session.add(layout)
            self.session.commit()
            self.session.refresh(layout)
            self.logger.info(f"Layout for {layout.line.name} line created")
            return {"id": layout.id}
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while creating layout '{line_id}': {e}")
            raise

    def get_layout_by_id(self, layout_id):
        return (self.session.query(LayoutModel)
                .options(
                    joinedload(LayoutModel.line),
                    joinedload(LayoutModel.line).joinedload(LineModel.factory),
                    joinedload(LayoutModel.user),
                    joinedload(LayoutModel.stations)
                )
                .filter(LayoutModel.id == layout_id).first())

    def get_all_layouts(self):
        return (self.session.query(LayoutModel)
                .options(
                    joinedload(LayoutModel.line),
                    joinedload(LayoutModel.line).joinedload(LineModel.factory),
                    joinedload(LayoutModel.stations)
                )
                .all())

    def get_layout_by_line_id(self, line_id):
        # Check for versions
        return (self.session.query(LayoutModel)
                .options(
                    joinedload(LayoutModel.line),
                    joinedload(LayoutModel.line).joinedload(LineModel.factory),
                    joinedload(LayoutModel.user),
                    joinedload(LayoutModel.stations)
                )
                .filter(LayoutModel.line_id == line_id).first())