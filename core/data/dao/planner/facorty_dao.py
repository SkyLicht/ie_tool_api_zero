from typing import List

from sqlalchemy.exc import SQLAlchemyError

from core.data.models.it_tool_orm_models import FactoryModel


class FactoryDAO:
    def __init__(self, session, logger):
        self.session = session
        self.logger = logger


    # add try except block
    def create_factory(self, factory: FactoryModel):
        self.session.add(factory)
        self.session.commit()
        self.logger.info(f"Factory {factory.name} created")

    def get_factory_by_name(self, name: str) -> FactoryModel:
        return self.session.query(FactoryModel).filter(FactoryModel.name == name).first()

    def get_all_factories(self) -> List[FactoryModel]:
        return self.session.query(FactoryModel).all()

    def delete_factory(self, factory: FactoryModel):
        self.session.delete(factory)
        self.session.commit()
        self.logger.info(f"Factory {factory.name} deleted")

    def update_factory(self, factory: FactoryModel):
        self.session.commit()
        self.logger.info(f"Factory {factory.name} updated")

    def create_all(self, factories: List[FactoryModel]):
        try:
            self.session.add_all(factories)
            self.session.commit()
            self.logger.info(f"Factories created")
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error while creating factories: {e}")
            raise
