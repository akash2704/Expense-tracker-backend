

def test_create_budget(client, db):
    """Test creating a budget for a user."""
    # Register and login
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    # Create a budget
    budget_data = {
        "category": "Trip to Paris",
        "limit": 1000.0
    }
    response = client.post("/budget/", json=budget_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    response_json = response.json()
    assert response_json["category"] == "Trip to Paris"
    assert response_json["limit"] == 1000.0
    assert response_json["user_id"] == 1
    assert response_json["spent"] == 0

def test_create_budget_unauthorized(client):
    """Test creating a budget without authentication."""
    budget_data = {
        "category": "Trip to Paris",
        "limit": 1000.0
    }
    response = client.post("/budget/", json=budget_data)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_get_budgets(client, db):
    """Test fetching budgets with spent amount."""
    # Register and login
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    # Create a budget
    budget_data = {
        "category": "Trip to Paris",
        "limit": 1000.0
    }
    budget_response = client.post("/budget/", json=budget_data, headers={"Authorization": f"Bearer {token}"})
    budget_id = budget_response.json()["id"]

    # Create expenses linked to the budget
    expense_data = {
        "amount": 500,
        "category": "Flight",
        "description": "Flight to Paris",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "transfer",
        "budget_id": budget_id
    }
    client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})

    expense_data2 = {
        "amount": 300,
        "category": "Hotel",
        "description": "Hotel in Paris",
        "type": "expense",
        "date": "2024-01-16T12:00:00",
        "payment_method": "transfer",
        "budget_id": budget_id
    }
    client.post("/expense/", json=expense_data2, headers={"Authorization": f"Bearer {token}"})

    # Create an income (should not affect spent)
    income_data = {
        "amount": 1000,
        "category": "Refund",
        "type": "income",
        "date": "2024-01-17T12:00:00",
        "payment_method": "transfer",
        "budget_id": budget_id
    }
    client.post("/expense/", json=income_data, headers={"Authorization": f"Bearer {token}"})

    # Fetch budgets
    response = client.get("/budget/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    budgets = response.json()
    assert len(budgets) == 1
    assert budgets[0]["category"] == "Trip to Paris"
    assert budgets[0]["limit"] == 1000.0
    assert budgets[0]["spent"] == 800  # 500 + 300 (only expenses count)

def test_get_budgets_unauthorized(client):
    """Test fetching budgets without authentication."""
    response = client.get("/budget/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_budget_no_expenses(client, db):
    """Test fetching a budget with no expenses."""
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    budget_data = {
        "category": "Trip to Paris",
        "limit": 1000.0
    }
    client.post("/budget/", json=budget_data, headers={"Authorization": f"Bearer {token}"})

    response = client.get("/budget/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    budgets = response.json()
    assert len(budgets) == 1
    assert budgets[0]["spent"] == 0

def test_budget_different_user(client, db):
    """Test that budgets are isolated per user."""
    # Create two users
    client.post("/auth/register", json={"username": "user1", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    client.post("/auth/register", json={"username": "user2", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})

    # Login as user1 and create a budget
    login_response1 = client.post("/auth/login", data={"username": "user1", "password": "securepass123"})
    token1 = login_response1.json()["access_token"]
    budget_data = {
        "category": "Trip to Paris",
        "limit": 1000.0
    }
    client.post("/budget/", json=budget_data, headers={"Authorization": f"Bearer {token1}"})

    # Login as user2 and check budgets
    login_response2 = client.post("/auth/login", data={"username": "user2", "password": "securepass123"})
    token2 = login_response2.json()["access_token"]
    response = client.get("/budget/", headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200
    assert len(response.json()) == 0  # User2 should have no budgets
