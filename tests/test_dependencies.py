from unittest.mock import patch

import pytest
from fastapi import HTTPException
from jose import jwt

from src.config import config
from src.dependencies import get_current_user
from src.models.user import User
from src.repositories.users_repo import create_user


def test_get_current_user_valid_token(db):
    """Test get_current_user with valid token"""
    # Create user
    user = User(username="testuser", hashed_password="hashedpass", bank_balance=10000, cash_balance=5000)
    created_user = create_user(db, user, initial_bank=10000, initial_cash=5000)

    # Create valid token
    token_data = {"sub": "testuser"}
    token = jwt.encode(token_data, config.SECRET_KEY, algorithm=config.ALGORITHM)

    # Mock get_user_by_username to return our user
    with patch('src.dependencies.get_user_by_username') as mock_get_user:
        mock_get_user.return_value = created_user
        current_user = get_current_user(token, db)
        assert current_user.username == "testuser"
        assert current_user.bank_balance == 10000
        assert current_user.cash_balance == 5000

def test_get_current_user_invalid_token(db):
    """Test get_current_user with invalid token"""
    invalid_token = "invalid.token.here"

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(invalid_token, db)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)

def test_get_current_user_no_username_in_token(db):
    """Test get_current_user with token missing username"""
    # Create token without 'sub' claim
    token_data = {"other_field": "value"}
    token = jwt.encode(token_data, config.SECRET_KEY, algorithm=config.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db)

    assert exc_info.value.status_code == 401

def test_get_current_user_user_not_found(db):
    """Test get_current_user when user doesn't exist"""
    # Create valid token for non-existent user
    token_data = {"sub": "nonexistent_user"}
    token = jwt.encode(token_data, config.SECRET_KEY, algorithm=config.ALGORITHM)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db)

    assert exc_info.value.status_code == 401
