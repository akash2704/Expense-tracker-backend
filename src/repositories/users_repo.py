import logging

from sqlalchemy.orm import Session

from src.models.user import User

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def get_user_by_username(db: Session, username: str):
    logger.info("Querying user: %s with session: %s, engine: %s", username, id(db), id(db.bind))
    result = db.query(User).filter(User.username == username).first()
    logger.info("Query result for %s: %s", username, result)
    return result

def create_user(db: Session, user: User, initial_bank: int, initial_cash: int):
    logger.info("Creating user: %s with session: %s, engine: %s, initial_bank: %s, initial_cash: %s", user.username, id(db), id(db.bind), initial_bank, initial_cash)
    user.bank_balance = initial_bank
    user.cash_balance = initial_cash
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created user: %s with balances bank: %s, cash: %s", user.username, user.bank_balance, user.cash_balance)
    return user
