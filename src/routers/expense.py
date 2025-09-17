import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.dependencies import get_current_user
from src.schemas.expense import Expense, ExpenseCreate, ExpenseUpdate
from src.schemas.users import User
from src.services.expense_service import (
    add_expense,
    delete_user_expense,
    get_user_balances,
    get_user_expenses,
    update_user_expense,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(prefix="/expense", tags=["expense"])

@router.post("/", response_model=Expense)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Expense:
    logger.info("Creating expense for user_id: %s with session: %s, engine: %s", current_user.id, id(db), id(db.bind))
    result = add_expense(db, expense, current_user.id)
    logger.info("Created expense with id: %s for user_id: %s", result.id, current_user.id)
    return result

@router.get("/", response_model=list[Expense])
def read_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Expense]:
    logger.info("Fetching expenses for user_id: %s with session: %s, engine: %s", current_user.id, id(db), id(db.bind))
    expenses = get_user_expenses(db, current_user.id, skip, limit)
    logger.info("Fetched %d expenses for user_id: %s", len(expenses), current_user.id)
    return expenses

@router.get("/balance")
def read_balance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, int]:
    logger.info("Fetching balance for user_id: %s with session: %s, engine: %s", current_user.id, id(db), id(db.bind))
    balances = get_user_balances(db, current_user.id)
    logger.info("Balances for user_id: %s are %s", current_user.id, balances)
    return balances

@router.patch("/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Expense:
    logger.info("Updating expense_id: %s for user_id: %s with session: %s, engine: %s", expense_id, current_user.id, id(db), id(db.bind))
    updated_expense = update_user_expense(db, expense_id, expense, current_user.id)
    if not updated_expense:
        logger.warning("Expense_id: %s not found or not owned by user_id: %s", expense_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found or not owned by user")
    logger.info("Updated expense_id: %s for user_id: %s", expense_id, current_user.id)
    return updated_expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    logger.info("Deleting expense_id: %s for user_id: %s with session: %s, engine: %s", expense_id, current_user.id, id(db), id(db.bind))
    success = delete_user_expense(db, expense_id, current_user.id)
    if not success:
        logger.warning("Expense_id: %s not found or not owned by user_id: %s", expense_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found or not owned by user")
    logger.info("Deleted expense_id: %s for user_id: %s", expense_id, current_user.id)
