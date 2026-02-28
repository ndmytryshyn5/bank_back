import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
def test_create_card():
    response = client.post("/cards/", json={
        "card_number": "1234567812345678",
        "card_holder": "Test User",
        "expiration_date": "2030-12-31",
        "cvv": "123",
        "balance": 100.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["card_holder"] == "Test User"
    assert data["balance"] == 100.0

def test_get_card():
    # Спочатку створимо картку
    create_response = client.post("/cards/", json={
        "card_number": "8765432187654321",
        "card_holder": "Another User",
        "expiration_date": "2031-01-01",
        "cvv": "321",
        "balance": 200.0
    })
    assert create_response.status_code == 201
    card_id = create_response.json()["id"]

    # Тепер отримаємо цю картку
    get_response = client.get(f"/cards/{card_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["card_holder"] == "Another User"
    assert data["balance"] == 200.0

def test_get_all_cards():
    response = client.get("/cards/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
