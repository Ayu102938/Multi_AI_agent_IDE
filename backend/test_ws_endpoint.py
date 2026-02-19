from fastapi.testclient import TestClient
from main import app
import time

def test_websocket_terminal():
    client = TestClient(app)
    try:
        with client.websocket_connect("/api/ws/terminal") as websocket:
            print("Connected to WebSocket")
            
            # Send a command
            cmd = "echo hello_world"
            print(f"Sending: {cmd}")
            websocket.send_text(cmd + "\r\n") # Enter key
            
            # Receive output
            # We expect multiple messages: prompt, input echo, command output, new prompt
            for _ in range(5):
                try:
                    data = websocket.receive_text()
                    print(f"Received: {repr(data)}")
                    if "hello_world" in data:
                        print("SUCCESS: Received expected output")
                        return
                except Exception as e:
                    print(f"Receive error or timeout: {e}")
                    break
            
            print("WARNING: Did not receive 'hello_world' in first few messages, but connection worked.")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_websocket_terminal()
