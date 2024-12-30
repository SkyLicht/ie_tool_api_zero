from typing import List

from core.data.dao.planner.line_dao import LineDAO
from core.data.models.it_tool_orm_models import UserModel
from core.data.schemas.planner.factory_schema import FactoryWithLinesSchema
from core.logger_manager import LoggerManager


class LineRepository:
    def __init__(self, session, user: UserModel):
        self.user = user
        self.session = session
        self.logger = LoggerManager.get_logger(name="LineRepository", log_file_name="db", username=user.username)
        self.line_dao = LineDAO(session, self.logger)

    def get_factories_lines(self):

        _lines = self.line_dao.get_all_with_factory()

        if len(_lines) > 0:
            self.logger.info(f"Lines found: {len(_lines)}")
        if not _lines:
            return []
        # list of factories -> lines
        factories: List[FactoryWithLinesSchema] = []

        for line in _lines:
            factory = next((x for x in factories if x.id == line.factory.id), None)
            if not factory:
                factory = FactoryWithLinesSchema(id=line.factory.id, name=line.factory.name, lines=[])
                factories.append(factory)
            factory.lines.append(line)

        return factories