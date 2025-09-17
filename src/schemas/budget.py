# src/schemas/budget.py

from pydantic import BaseModel, ConfigDict


class BudgetBase(BaseModel):
    category: str
    limit: float

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    user_id: int
    spent: int = 0  # Computed spent amount in cents

    model_config = ConfigDict(from_attributes=True)
