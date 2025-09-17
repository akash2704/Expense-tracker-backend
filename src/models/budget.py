from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    limit = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))

    expenses = relationship("Expense", back_populates="budget")
    owner = relationship("User", back_populates="budgets")
