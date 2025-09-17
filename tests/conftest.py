import logging
import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/tests_output.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def pytest_configure(config):
    """Set up test environment before running tests"""
    os.environ["TEST_ENV"] = "1"

def pytest_unconfigure(config):
    """Clean up test environment after running tests"""
    os.environ.pop("TEST_ENV", None)

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine for the entire test session"""
    # Create engine for in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Import the Base and models to ensure they're registered
    from src.db.database import Base

    logger.info("Models registered with Base: %s", list(Base.metadata.tables.keys()))

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created: %s", list(Base.metadata.tables.keys()))

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    """Create a database session for each test function"""
    connection = db_engine.connect()
    transaction = connection.begin()

    # Create session bound to connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override"""
    # Import here to avoid circular imports
    from src.db.database import get_db
    from src.main import app

    def override_get_db() -> Generator[Session, None, None]:
        try:
            logger.info("Overriding get_db with session: %s, engine: %s", id(db), id(db.bind))
            yield db
        finally:
            logger.info("Test database session provided: %s", id(db))

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides.clear()
