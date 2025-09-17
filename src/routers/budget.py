# src/routers/budget.py

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.dependencies import get_current_user
from src.models.expense import Expense
from src.schemas.budget import Budget, BudgetCreate
from src.schemas.users import User
from src.services.budget_service import create_user_budget, get_user_budgets

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(prefix="/budget", tags=["budget"])

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
def create_budget_endpoint(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Budget:
    """Create a new budget for the current user."""
    logger.info("Endpoint: Creating budget for user_id: %s", current_user.id)
    return create_user_budget(db, budget, current_user.id)


@router.get("/", response_model=list[Budget])
def read_budgets_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Budget]:
    """Retrieve all budgets for the current user, with spent amount."""
    logger.info("Endpoint: Fetching budgets for user_id: %s", current_user.id)
    budgets = get_user_budgets(db, current_user.id)
    for budget in budgets:
        spent = db.query(func.sum(Expense.amount)).filter(Expense.budget_id == budget.id, Expense.type == "expense").scalar() or 0
        budget.spent = spent  # Add dynamic field
    return budgets
