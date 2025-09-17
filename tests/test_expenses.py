def test_create_expense(client):
    # Register and login
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    # Create expense with date
    expense_data = {
        "amount": 500,
        "category": "Food",
        "description": "Lunch",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    response = client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["amount"] == 500
    assert response_json["category"] == "Food"
    assert response_json["user_id"] == 1
    assert response_json["payment_method"] == "cash"

def test_list_expenses(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    expense_data = {
        "amount": 500,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/expense/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 500

def test_get_balance(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    expense_data = {
        "amount": 500,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/expense/balance", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"bank_balance": 10000, "cash_balance": 4500, "total_balance": 14500}

def test_update_expense(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    expense_data = {
        "amount": 500,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    create_response = client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    expense_id = create_response.json()["id"]

    response = client.patch(f"/expense/{expense_id}", json={"amount": 600, "category": "Dining", "payment_method": "transfer"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["amount"] == 600
    assert response.json()["category"] == "Dining"
    assert response.json()["payment_method"] == "transfer"

def test_delete_expense(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    expense_data = {
        "amount": 500,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    create_response = client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    expense_id = create_response.json()["id"]

    response = client.delete(f"/expense/{expense_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    list_response = client.get("/expense/", headers={"Authorization": f"Bearer {token}"})
    assert len(list_response.json()) == 0

def test_expense_affects_balance_correctly(client):
    """Test that expenses and income affect balance correctly"""
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    # Initial balances
    response = client.get("/expense/balance", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"bank_balance": 10000, "cash_balance": 5000, "total_balance": 15000}

    # Add cash expense
    expense_data = {
        "amount": 500,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})

    # Cash decreases
    response = client.get("/expense/balance", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"bank_balance": 10000, "cash_balance": 4500, "total_balance": 14500}

    # Add transfer income
    income_data = {
        "amount": 1000,
        "category": "Salary",
        "type": "income",
        "date": "2024-01-15T12:00:00",
        "payment_method": "transfer"
    }
    client.post("/expense/", json=income_data, headers={"Authorization": f"Bearer {token}"})

    # Bank increases
    response = client.get("/expense/balance", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"bank_balance": 11000, "cash_balance": 4500, "total_balance": 15500}

def test_insufficient_funds(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 100, "initial_cash": 100})
    login_response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    token = login_response.json()["access_token"]

    expense_data = {
        "amount": 200,
        "category": "Food",
        "type": "expense",
        "date": "2024-01-15T12:00:00",
        "payment_method": "cash"
    }
    response = client.post("/expense/", json=expense_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]
