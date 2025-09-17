def test_register(client):
    response = client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    assert response.status_code == 201
    assert response.json() == {
        "username": "testuser",
        "id": 1,
        "is_active": True,
        "bank_balance": 10000,
        "cash_balance": 5000
    }

def test_register_duplicate_username(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    response = client.post("/auth/register", json={"username": "testuser", "password": "anotherpass", "initial_bank": 10000, "initial_cash": 5000})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login(client):
    client.post("/auth/register", json={"username": "testuser", "password": "securepass123", "initial_bank": 10000, "initial_cash": 5000})
    response = client.post("/auth/login", data={"username": "testuser", "password": "securepass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={"username": "testuser", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
