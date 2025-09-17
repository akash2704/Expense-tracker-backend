# src/services/budget_service.py

import logging

from sqlalchemy.orm import Session

from src.repositories.budget_repo import create_budget, get_budgets_by_user
from src.schemas.budget import Budget, BudgetCreate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def create_user_budget(db: Session, budget_data: BudgetCreate, user_id: int) -> Budget:
    """Service to create a new budget for a user."""
    logger.info("Service: Creating budget for user_id: %s with category: %s", user_id, budget_data.category)
    return create_budget(db, budget_data, user_id)


def get_user_budgets(db: Session, user_id: int) -> list[Budget]:
    """Service to retrieve all budgets for a user."""
    logger.info("Service: Fetching budgets for user_id: %s", user_id)
    return get_budgets_by_user(db, user_id)
