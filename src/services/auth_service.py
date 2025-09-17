import logging
from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from src.config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.info("Verifying password for hashed_password: %s", hashed_password[:10] + "...")
    result = pwd_context.verify(plain_password, hashed_password)
    logger.info("Password verification result: %s", result)
    return result

def get_password_hash(password: str) -> str:
    logger.info("Hashing password")
    hashed = pwd_context.hash(password)
    logger.info("Password hashed: %s", hashed[:10] + "...")
    return hashed

def create_access_token(data: dict[str, str]) -> str:
    logger.info("Creating access token for data: %s", data)
    to_encode: dict[str, str | datetime] = data.copy()
    # Fix: Use timezone-aware datetime instead of deprecated utcnow()
    expire: datetime = datetime.now(UTC) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    logger.info("Access token created: %s", encoded_jwt[:10] + "...")
    return encoded_jwt
