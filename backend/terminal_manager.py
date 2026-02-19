import asyncio
import os
import sys
import subprocess
from fastapi import WebSocket

class TerminalManager:
    def __init__(self):
        self.process = None
        self.websocket = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.websocket = websocket
        await self.start_shell()

    async def start_shell(self):
        # Use PowerShell on Windows, bash on others (simplified for Windows env)
        shell_cmd = "powershell.exe" if os.name == 'nt' else "bash"
        
        # Create subprocess with pipes
        # We need to use asyncio.create_subprocess_exec for non-blocking I/O
        self.process = await asyncio.create_subprocess_exec(
            shell_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Create a new console window group so signals don't propagate to parent
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )

        # Start background tasks to read stdout/stderr
        asyncio.create_task(self._read_stream(self.process.stdout))
        asyncio.create_task(self._read_stream(self.process.stderr))

    async def _read_stream(self, stream):
        while True:
            try:
                # Read 1024 bytes at a time
                data = await stream.read(1024)
                if not data:
                    break
                # Send raw bytes or decode? xterm.js handles strings well.
                # Decoding might fail if cut in middle of multibyte char, 
                # but for simplicity let's try decoding with errors='replace'.
                # Better: send text if possible.
                text = data.decode('cp932', errors='replace') # Windows typically uses cp932 (Shift-JIS) or utf-8
                # If pure utf-8 environment, change to utf-8. 
                # PowerShell might output local encoding. 
                # Let's try to detect or default to cp932 for Japanese Windows.
                
                await self.websocket.send_text(text)
            except Exception as e:
                print(f"Error reading stream: {e}")
                break

    async def write(self, data: str):
        if self.process and self.process.stdin:
            # Encode string to bytes
            # PowerShell expects input in local encoding or UTF-8 depending on config.
            # Let's try local encoding (cp932) first.
            try:
                self.process.stdin.write(data.encode('cp932'))
                await self.process.stdin.drain()
            except Exception:
                # Fallback to utf-8
                self.process.stdin.write(data.encode('utf-8'))
                await self.process.stdin.drain()

    async def disconnect(self):
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
            self.process = None
