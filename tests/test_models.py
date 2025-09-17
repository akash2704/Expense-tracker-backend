
from datetime import UTC, datetime

from src.models.expense import Expense
from src.models.user import User


def test_user_model_creation(db):
    """Test User model creation and attributes"""
    user = User(
        username="testuser",
        hashed_password="hashedpassword",
        is_active=True,
        bank_balance=10000,
        cash_balance=5000
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword"
    assert user.is_active is True
    assert user.bank_balance == 10000
    assert user.cash_balance == 5000

def test_expense_model_creation(db):
    """Test Expense model creation and attributes"""
    # Create user first
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    expense = Expense(
        amount=750,  # Changed to integer (cents)
        category="Transportation",
        description="Bus fare",
        date=datetime.now(UTC),
        type="expense",
        user_id=user.id,
        payment_method="cash"
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    assert expense.id is not None
    assert expense.amount == 750
    assert expense.category == "Transportation"
    assert expense.description == "Bus fare"
    assert expense.type == "expense"
    assert expense.user_id == user.id
    assert expense.payment_method == "cash"
