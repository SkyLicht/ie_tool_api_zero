from core.data.models.it_tool_orm_models import OperationModel


class OperationDAO:
    def __init__(self, session, logger):
        self.session = session
        self.logger = logger


    def get_all_operations(self):
        return self.session.query(OperationModel).all()