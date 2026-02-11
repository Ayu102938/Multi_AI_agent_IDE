from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_endpoint():
    # Test Payload
    payload = {"message": "Hello AI"}
    
    # Expecting a POST request to /api/chat
    response = client.post("/api/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    # Ideally, it should return something from the agents
    # For now, we expect a placeholder or mock response
