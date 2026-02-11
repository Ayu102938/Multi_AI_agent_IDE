import httpx
import sys

try:
    # Test List Files
    print("Testing GET /api/files...")
    response = httpx.get("http://localhost:8000/api/files")
    if response.status_code == 200:
        print("List Files: SUCCESS")
        print(response.json())
    else:
        print(f"List Files: FAILED ({response.status_code})")
        print(response.text)

    # Test Read File
    print("\nTesting GET /api/files/test.txt...")
    response = httpx.get("http://localhost:8000/api/files/test.txt")
    if response.status_code == 200:
        print("Read File: SUCCESS")
        print(response.json())
    else:
        print(f"Read File: FAILED ({response.status_code})")
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
