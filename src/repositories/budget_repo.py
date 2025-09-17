
import logging

from sqlalchemy.orm import Session

from src.models.budget import Budget
from src.schemas.budget import BudgetCreate

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('logs/tests.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_budget(db: Session, budget_data: BudgetCreate, user_id: int):
    """Create a new budget for a user."""
    logger.info("Creating budget for user_id: %s with category: %s", user_id, budget_data.category)
    db_budget = Budget(
        category=budget_data.category,
        limit=budget_data.limit,
        user_id=user_id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    logger.info("Created budget with id: %s", db_budget.id)
    return db_budget

def get_budgets_by_user(db: Session, user_id: int):
    """Retrieve all budgets for a given user."""
    logger.info("Fetching budgets for user_id: %s", user_id)
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    logger.info("Fetched %d budgets for user_id: %s", len(budgets), user_id)
    return budgets

def get_budget_by_id(db: Session, budget_id: int, user_id: int):
    """Retrieve a specific budget by its ID and user ID."""
    logger.info("Fetching budget_id: %s for user_id: %s", budget_id, user_id)
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    logger.info("Budget_id: %s found: %s", budget_id, bool(budget))
    return budget
