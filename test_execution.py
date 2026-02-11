import requests
import sys

BASE_URL = "http://localhost:8000"

def test_run():
    print("Testing Code Execution with Import...")
    
    code = """
import sys
import os
print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")
try:
    import example
    example.hello()
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
"""
    
    try:
        response = requests.post(f"{BASE_URL}/api/run", json={"code": code})
        response.raise_for_status()
        result = response.json()
        print("Response:", result)
        
        output = result.get("output", "")
        if "Hello from workspace!" in output:
            print("SUCCESS: Import worked!")
        else:
            print("FAILURE: Import did not work.")
            
    except Exception as e:
        print(f"Request FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_run()
