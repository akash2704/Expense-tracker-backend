import logging
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import config

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests_output.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

Base = declarative_base()

# Initialize engine and session maker as None
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection"""
    global engine, SessionLocal

    # --- Move model imports inside this function ---

    if engine is None:
        # Determine database URL based on environment
        if os.getenv("TEST_ENV"):
            DATABASE_URL = "sqlite:///:memory:"
        else:
            DATABASE_URL = config.DATABASE_URL

        logger.info("Creating engine with DATABASE_URL: %s", DATABASE_URL)

        # Create engine with appropriate settings
        if "sqlite" in DATABASE_URL:
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(DATABASE_URL)

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create tables if using in-memory database
        if "memory" in DATABASE_URL:
            # Import models to ensure they are registered
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created in in-memory database: %s", list(Base.metadata.tables.keys()))

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    # Initialize database if not already done
    init_database()

    db: Session = SessionLocal()
    try:
        logger.info("Providing database session: %s, engine: %s", id(db), id(db.bind))
        yield db
    finally:
        db.close()
        logger.info("Closed database session: %s", id(db))
