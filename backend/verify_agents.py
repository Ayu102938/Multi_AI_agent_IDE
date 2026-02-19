import requests
import time

def test_agent_api():
    url = "http://localhost:8000/api/chat"
    payload = {"message": "Hello, are you ready?"}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Backend API accepted the request.")
            print("Agents are starting in the background. Check backend logs for activity.")
        else:
            print("FAILURE: Backend returned unexpected status.")
            
    except Exception as e:
        print(f"ERROR: Could not connect to backend. {e}")

if __name__ == "__main__":
    test_agent_api()
