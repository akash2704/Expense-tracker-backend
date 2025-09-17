
from datetime import UTC, datetime

from src.models.expense import Expense
from src.models.user import User
from src.repositories.expense_repo import (
    create_expense,
    delete_expense,
    get_balances,  # Updated from get_balance
    get_expense_by_id,
    get_expenses,
    update_expense,
)
from src.repositories.users_repo import create_user, get_user_by_username


def test_create_and_get_user_repo(db):
    """Test user repository functions"""
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    created_user = create_user(db, user, initial_bank=10000, initial_cash=5000)

    assert created_user.id is not None
    assert created_user.username == "testuser"
    assert created_user.bank_balance == 10000
    assert created_user.cash_balance == 5000

    # Test getting user by username
    retrieved_user = get_user_by_username(db, "testuser")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"

def test_get_nonexistent_user(db):
    """Test getting non-existent user"""
    user = get_user_by_username(db, "nonexistent")
    assert user is None

def test_expense_repository_functions(db):
    """Test expense repository functions"""
    # Create user first
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create expense
    expense = Expense(
        amount=500,  # Changed to integer (cents)
        category="Food",
        type="expense",
        date=datetime.now(UTC),
        user_id=user.id,
        payment_method="cash"
    )

    created_expense = create_expense(db, expense)
    assert created_expense.id is not None

    # Test get expenses
    expenses = get_expenses(db, user.id)
    assert len(expenses) == 1
    assert expenses[0].amount == 500

    # Test get balances
    balances = get_balances(db, user.id)
    assert balances == {"bank_balance": 10000, "cash_balance": 5000, "total_balance": 15000}

    # Test get expense by id
    retrieved_expense = get_expense_by_id(db, created_expense.id, user.id)
    assert retrieved_expense is not None
    assert retrieved_expense.amount == 500

    # Test update expense
    retrieved_expense.amount = 600
    retrieved_expense.payment_method = "transfer"
    updated_expense = update_expense(db, retrieved_expense)
    assert updated_expense.amount == 600
    assert updated_expense.payment_method == "transfer"

    # Test delete expense
    delete_expense(db, updated_expense)
    deleted_expense = get_expense_by_id(db, updated_expense.id, user.id)
    assert deleted_expense is None

def test_get_balances_nonexistent_user(db):
    """Test getting balances for non-existent user"""
    balances = get_balances(db, 999)
    assert balances == {"bank_balance": 0, "cash_balance": 0, "total_balance": 0}

def test_get_expense_wrong_user(db):
    """Test getting expense with wrong user ID"""
    # Create two users
    user1 = User(username="user1", hashed_password="hash1", bank_balance=10000, cash_balance=5000)
    user2 = User(username="user2", hashed_password="hash2", bank_balance=10000, cash_balance=5000)
    db.add(user1)
    db.add(user2)
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    # Create expense for user1
    expense = Expense(
        amount=500,
        category="Food",
        type="expense",
        date=datetime.now(UTC),
        user_id=user1.id,
        payment_method="cash"
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    # Try to get expense as user2
    retrieved_expense = get_expense_by_id(db, expense.id, user2.id)
    assert retrieved_expense is None
