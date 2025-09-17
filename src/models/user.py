from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.database import Base


class User(Base):
    __tablename__: str = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    bank_balance = Column(Integer, default=0)  # In cents
    cash_balance = Column(Integer, default=0)  # In cents

    expenses = relationship("Expense", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")
