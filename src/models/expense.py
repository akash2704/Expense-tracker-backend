from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class Expense(Base):
    __tablename__: str = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)  # In cents
    category = Column(String)
    description = Column(String)
    date = Column(DateTime)
    type = Column(String)  # "expense" or "income"
    user_id = Column(Integer, ForeignKey("users.id"))
    # New field to track payment method
    payment_method = Column(String, default="cash")
    # New field to link to a budget
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=True)

    owner = relationship("User", back_populates="expenses")
    budget = relationship("Budget", back_populates="expenses")
