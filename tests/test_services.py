from datetime import UTC, datetime

import pytest

from src.models.expense import Expense
from src.models.user import User
from src.schemas.expense import ExpenseCreate, ExpenseUpdate
from src.services.auth_service import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.services.expense_service import (
    add_expense,
    delete_user_expense,
    update_user_expense,
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser"}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

def test_add_expense_service(db):
    """Test adding expense through service layer"""
    # Create user first
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    expense_data = ExpenseCreate(
        amount=500,  # Changed to integer (cents)
        category="Food",
        description="Test expense",
        type="expense",
        date=datetime.now(UTC),
        payment_method="cash"
    )

    expense = add_expense(db, expense_data, user.id)

    assert expense.amount == 500
    assert expense.category == "Food"
    assert expense.user_id == user.id
    assert expense.payment_method == "cash"

    # Verify balance update
    db.refresh(user)
    assert user.cash_balance == 4500
    assert user.bank_balance == 10000

def test_add_income_service(db):
    """Test adding income through service layer"""
    # Create user first
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    income_data = ExpenseCreate(
        amount=1000,
        category="Salary",
        description="Monthly salary",
        type="income",
        date=datetime.now(UTC),
        payment_method="transfer"
    )

    add_expense(db, income_data, user.id)

    # Refresh user to get updated balance
    db.refresh(user)
    assert user.bank_balance == 11000
    assert user.cash_balance == 5000

def test_user_not_found_error(db):
    """Test error when user doesn't exist"""
    expense_data = ExpenseCreate(
        amount=500,
        category="Food",
        type="expense",
        date=datetime.now(UTC),
        payment_method="cash"
    )

    with pytest.raises(ValueError, match="User not found"):
        add_expense(db, expense_data, 999)  # Non-existent user ID

def test_update_expense_service(db):
    """Test updating expense through service layer"""
    # Create user and expense
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    expense = Expense(
        amount=500,
        category="Food",
        type="expense",
        date=datetime.now(UTC),
        user_id=user.id,
        payment_method="cash"
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    update_data = ExpenseUpdate(amount=600, category="Dining", payment_method="transfer")
    updated_expense = update_user_expense(db, expense.id, update_data, user.id)

    assert updated_expense.amount == 600
    assert updated_expense.category == "Dining"
    assert updated_expense.payment_method == "transfer"

    # Verify balance update (cash +500, bank -600)
    db.refresh(user)
    assert user.cash_balance == 5500
    assert user.bank_balance == 9400

def test_update_nonexistent_expense(db):
    """Test updating non-existent expense"""
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    update_data = ExpenseUpdate(amount=600)
    result = update_user_expense(db, 999, update_data, user.id)

    assert result is None

def test_delete_expense_service(db):
    """Test deleting expense through service layer"""
    # Create user and expense
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    expense = Expense(
        amount=500,
        category="Food",
        type="expense",
        date=datetime.now(UTC),
        user_id=user.id,
        payment_method="cash"
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    result = delete_user_expense(db, expense.id, user.id)
    assert result is True

    # Verify expense is deleted
    deleted_expense = db.query(Expense).filter(Expense.id == expense.id).first()
    assert deleted_expense is None

    # Verify balance update
    db.refresh(user)
    assert user.cash_balance == 5500
    assert user.bank_balance == 10000

def test_delete_nonexistent_expense(db):
    """Test deleting non-existent expense"""
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    result = delete_user_expense(db, 999, user.id)
    assert result is False
