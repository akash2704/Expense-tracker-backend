from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in cents, must be positive")
    category: str = Field(..., min_length=1, max_length=50, description="Category, e.g., Food, Travel")
    description: str | None = Field(None, max_length=200, description="Optional description")
    type: str = Field(..., pattern="^(expense|income)$", description="Type: expense or income")
    # Field for payment method with validation
    payment_method: str = Field(default="cash", pattern="^(cash|transfer)$", description="Payment method: cash or transfer")
    # Field to link to a budget
    budget_id: int | None = Field(None, description="Optional budget ID to associate with this expense")


class ExpenseCreate(ExpenseBase):
    date: datetime = Field(..., description="Date of transaction")

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdate(BaseModel):
    amount: int | None = Field(None, gt=0, description="Amount in cents, must be positive")
    category: str | None = Field(None, min_length=1, max_length=50, description="Category, e.g., Food, Travel")
    description: str | None = Field(None, max_length=200, description="Optional description")
    type: str | None = Field(None, pattern="^(expense|income)$", description="Type: expense or income")
    date: datetime | None = Field(None, description="Date of transaction")
    # Field for payment method
    payment_method: str | None = Field(None, pattern="^(cash|transfer)$")
    # Field to link to a budget
    budget_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class Expense(ExpenseBase):
    id: int
    date: datetime
    user_id: int
    # Ensure payment_method and budget_id are included in the response schema
    payment_method: str
    budget_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
