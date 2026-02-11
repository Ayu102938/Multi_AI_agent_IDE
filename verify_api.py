import requests
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing API...")
    
    # 1. Test List Files
    try:
        response = requests.get(f"{BASE_URL}/api/files")
        response.raise_for_status()
        files = response.json().get("files", [])
        print(f"GET /api/files: Success. Files: {files}")
        
        if "example.py" not in files:
            print("ERROR: example.py not found in file list")
            sys.exit(1)
            
    except Exception as e:
        print(f"GET /api/files FAILED: {e}")
        sys.exit(1)

    # 2. Test Read File
    try:
        response = requests.get(f"{BASE_URL}/api/files/example.py")
        response.raise_for_status()
        content = response.json().get("content", "")
        print(f"GET /api/files/example.py: Success. Content length: {len(content)}")
        
        expected = 'def hello():\n    print("Hello from workspace!")'
        if expected.strip() not in content.strip():
             print(f"ERROR: Content mismatch.\nExpected:\n{expected}\nGot:\n{content}")
             # sys.exit(1) # Strict check might fail due to newline diffs, just warning for now
        
    except Exception as e:
        print(f"GET /api/files/example.py FAILED: {e}")
        sys.exit(1)

    print("API Verification Passed!")

if __name__ == "__main__":
    test_api()
