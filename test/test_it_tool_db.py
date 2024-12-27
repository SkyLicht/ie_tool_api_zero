import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from core.db.ie_tool_db import Base

TEST_DATABASE_URL = "sqlite:///:memory:"  # In-memory DB

# Create the engine and session for testing
engine_test = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """
    Create the database schema before running tests.
    Drop tables after tests are done.
    """
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    """
    Returns a SQLAlchemy session for use in individual tests.
    Rollbacks changes after each test.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# @pytest.fixture
# def client(db_session):
#     """
#     Override the get_db dependency to use the test DB session.
#     Return a TestClient that uses the FastAPI core.
#     """
#
#     def _get_test_db():
#         try:
#             yield db_session
#         finally:
#             pass
#
#     # Override dependency in the FastAPI core
#     core.dependency_overrides[get_db] = _get_test_db
#
#     with TestClient(core) as c:
#         yield c
