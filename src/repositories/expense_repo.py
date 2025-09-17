import logging

from sqlalchemy.orm import Session

from src.models.expense import Expense
from src.models.user import User

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_expense(db: Session, expense: Expense):
    logger.info("Creating expense with id: %s for user_id: %s with session: %s", expense.id, expense.user_id, id(db))
    db.add(expense)
    db.commit()
    db.refresh(expense)
    logger.info("Created expense with id: %s", expense.id)
    return expense

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    logger.info("Fetching expenses for user_id: %s with session: %s, skip: %s, limit: %s", user_id, id(db), skip, limit)
    expenses = db.query(Expense).filter(Expense.user_id == user_id).offset(skip).limit(limit).all()
    logger.info("Fetched %d expenses for user_id: %s", len(expenses), user_id)
    return expenses

def get_balances(db: Session, user_id: int):
    logger.info("Fetching balances for user_id: %s with session: %s", user_id, id(db))
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        balances = {
            "bank_balance": user.bank_balance,
            "cash_balance": user.cash_balance,
            "total_balance": user.bank_balance + user.cash_balance
        }
        logger.info("Balances for user_id: %s are %s", user_id, balances)
        return balances
    logger.warning("User not found for balances: user_id %s", user_id)
    return {"bank_balance": 0, "cash_balance": 0, "total_balance": 0}

def get_expense_by_id(db: Session, expense_id: int, user_id: int):
    logger.info("Fetching expense_id: %s for user_id: %s with session: %s", expense_id, user_id, id(db))
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
    logger.info("Expense_id: %s found: %s", expense_id, bool(expense))
    return expense

def update_expense(db: Session, expense: Expense):
    logger.info("Updating expense_id: %s with session: %s", expense.id, id(db))
    db.commit()
    db.refresh(expense)
    logger.info("Updated expense_id: %s", expense.id)
    return expense

def delete_expense(db: Session, expense: Expense):
    logger.info("Deleting expense_id: %s with session: %s", expense.id, id(db))
    db.delete(expense)
    db.commit()
    logger.info("Deleted expense_id: %s", expense.id)
