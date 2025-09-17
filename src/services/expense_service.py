import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.expense import Expense
from src.models.user import User
from src.repositories.expense_repo import (
    create_expense,
    delete_expense,
    get_balances,
    get_expense_by_id,
    get_expenses,
    update_expense,
)
from src.schemas.expense import ExpenseCreate, ExpenseUpdate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def get_balance_field(payment_method: str) -> str:
    if payment_method == "cash":
        return "cash_balance"
    elif payment_method == "transfer":
        return "bank_balance"
    raise ValueError("Invalid payment_method")


def add_expense(db: Session, expense_data: ExpenseCreate, user_id: int) -> Expense:
    logger.info("Adding expense for user_id: %s with session: %s, engine: %s", user_id, id(db), id(db.bind))
    expense: Expense = Expense(
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        date=expense_data.date,
        type=expense_data.type,
        user_id=user_id,
        payment_method=expense_data.payment_method,
        budget_id=expense_data.budget_id
    )
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error("User not found: user_id %s", user_id)
        raise ValueError("User not found")
    balance_field = get_balance_field(expense.payment_method)
    current_balance = getattr(user, balance_field)
    if expense.type == "expense":
        if current_balance < expense.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        setattr(user, balance_field, current_balance - expense.amount)
    elif expense.type == "income":
        setattr(user, balance_field, current_balance + expense.amount)
    db.commit()
    logger.info("User balances updated: user_id %s, %s: %d", user_id, balance_field, getattr(user, balance_field))
    result = create_expense(db, expense)
    logger.info("Expense added: id %s for user_id %s", result.id, user_id)
    return result


def get_user_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Expense]:
    logger.info("Fetching user expenses for user_id: %s with session: %s", user_id, id(db))
    expenses = get_expenses(db, user_id, skip, limit)
    logger.info("Fetched %d expenses for user_id: %s", len(expenses), user_id)
    return expenses


def get_user_balances(db: Session, user_id: int) -> dict[str, int]:
    logger.info("Fetching user balances for user_id: %s with session: %s", user_id, id(db))
    balances = get_balances(db, user_id)
    logger.info("Balances for user_id: %s are %s", user_id, balances)
    return balances


def update_user_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate, user_id: int) -> Expense | None:
    logger.info("Updating expense_id: %s for user_id: %s with session: %s", expense_id, user_id, id(db))
    expense: Expense | None = get_expense_by_id(db, expense_id, user_id)
    if not expense:
        logger.warning("Expense_id: %s not found for user_id: %s", expense_id, user_id)
        return None
    old_amount: int = expense.amount
    old_type: str = expense.type
    old_payment_method: str = expense.payment_method
    old_balance_field = get_balance_field(old_payment_method)
    # Apply updates
    for field, value in expense_data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error("User not found: user_id %s", user_id)
        raise ValueError("User not found")
    # Reverse old adjustment
    if old_type == "expense":
        setattr(user, old_balance_field, getattr(user, old_balance_field) + old_amount)
    elif old_type == "income":
        setattr(user, old_balance_field, getattr(user, old_balance_field) - old_amount)
    # Apply new adjustment
    new_balance_field = get_balance_field(expense.payment_method)
    new_current_balance = getattr(user, new_balance_field)
    if expense.type == "expense":
        if new_current_balance < expense.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
        setattr(user, new_balance_field, new_current_balance - expense.amount)
    elif expense.type == "income":
        setattr(user, new_balance_field, new_current_balance + expense.amount)
    db.commit()
    logger.info("User balances updated: user_id %s, %s: %d", user_id, new_balance_field, getattr(user, new_balance_field))
    result = update_expense(db, expense)
    logger.info("Updated expense_id: %s for user_id %s", expense_id, user_id)
    return result


def delete_user_expense(db: Session, expense_id: int, user_id: int) -> bool:
    logger.info("Deleting expense_id: %s for user_id: %s with session: %s", expense_id, user_id, id(db))
    expense: Expense | None = get_expense_by_id(db, expense_id, user_id)
    if not expense:
        logger.warning("Expense_id: %s not found for user_id: %s", expense_id, user_id)
        return False
    user: User | None = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error("User not found: user_id %s", user_id)
        raise ValueError("User not found")
    balance_field = get_balance_field(expense.payment_method)
    if expense.type == "expense":
        setattr(user, balance_field, getattr(user, balance_field) + expense.amount)
    elif expense.type == "income":
        setattr(user, balance_field, getattr(user, balance_field) - expense.amount)
    db.commit()
    logger.info("User balances updated: user_id %s, %s: %d", user_id, balance_field, getattr(user, balance_field))
    delete_expense(db, expense)
    logger.info("Deleted expense_id: %s for user_id %s", expense_id, user_id)
    return True
