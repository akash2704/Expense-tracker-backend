# tests/test_main.py

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Expense Tracker API is running"}

def test_health_check_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_unauthorized_expense_access(client):
    """Test accessing expense endpoints without authentication"""
    response = client.get("/expense/")
    assert response.status_code == 401

    response = client.post("/expense/", json={"amount": 100, "category": "test", "type": "expense"})
    assert response.status_code == 401
