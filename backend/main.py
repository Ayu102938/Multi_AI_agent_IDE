from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from dotenv import load_dotenv

# Absolute path to .env file relative to this script
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Ensure workspace directory exists
    workspace_path = Path(__file__).resolve().parent / "workspace"
    if not workspace_path.exists():
        workspace_path.mkdir(parents=True, exist_ok=True)
        print(f"Workspace directory initialized at: {workspace_path.absolute()}")

from pydantic import BaseModel

from fastapi import BackgroundTasks
from logger import agent_logger
import asyncio
from agents import create_agents
from crewai import Crew, Process, Task

class ChatRequest(BaseModel):
    message: str

import re

def extract_and_save_code_blocks(text: str, workspace_path: Path) -> list:
    """
    Extract code blocks from agent text output and save them as files.
    This is a fallback for when agents output code as text
    instead of using File Writer Tool.
    
    Returns list of saved filenames.
    """
    saved_files = []
    
    # Find all code blocks with language hints
    pattern = r'```(\w+)?\n(.*?)```'
    blocks = list(re.finditer(pattern, text, re.DOTALL))
    
    if not blocks:
        return saved_files
    
    # Map of language to file extension
    ext_map = {
        'python': '.py',
        'py': '.py',
        'javascript': '.js',
        'js': '.js',
        'typescript': '.ts',
        'ts': '.ts',
        'html': '.html',
        'css': '.css',
        'json': '.json',
        'yaml': '.yaml',
        'yml': '.yml',
        'markdown': '.md',
        'md': '.md',
        'txt': '.txt',
        'sh': '.sh',
        'bash': '.sh',
        'sql': '.sql',
    }
    
    for i, match in enumerate(blocks):
        lang = (match.group(1) or '').lower()
        content = match.group(2).strip()
        
        if not content or lang in ('', 'text', 'plaintext'):
            continue
        
        # Skip non-code blocks (e.g. file structure diagrams)
        if lang not in ext_map:
            continue
        
        ext = ext_map[lang]
        
        # Try to detect filename from content
        filename = None
        
        # Method 1: Look for filename in comments at the top
        # e.g. "# filename: calculator.py" or "# calculator.py"
        first_lines = content.split('\n')[:5]
        for line in first_lines:
            # Match patterns like: # calculator.py, # filename: calculator.py
            fname_match = re.search(r'#\s*(?:filename:\s*)?(\w[\w\-]*\.\w+)', line, re.IGNORECASE)
            if fname_match:
                candidate = fname_match.group(1)
                # Verify it has a reasonable extension
                if '.' in candidate:
                    filename = candidate
                    break
        
        # Method 2: Look for module docstring hints
        if not filename:
            for line in first_lines:
                # Match: """Calculator module...""" -> calculator.py
                doc_match = re.search(r'["\']+(.*?module.*?|.*?for (?:the )?(\w+))', line, re.IGNORECASE)
                if doc_match:
                    break
        
        # Method 3: Look at text before the code block for filename
        if not filename:
            pre_text = text[:match.start()]
            # Look for ### 3.1 main.py or similar headings
            heading_match = re.findall(r'#+\s+(?:\d+\.?\d*\s+)?(\w[\w\-]*\.\w+)', pre_text)
            if heading_match:
                filename = heading_match[-1]  # Take the most recent match
        
        # Method 4: Look for "file: X" or "save as X" patterns before block
        if not filename:
            pre_text_short = text[max(0, match.start()-200):match.start()]
            save_match = re.search(r'(?:file|save|create|ファイル)[\s:]*[`"]?(\w[\w\-]*\.\w+)', pre_text_short, re.IGNORECASE)
            if save_match:
                filename = save_match.group(1)
        
        # Fallback: generate a filename
        if not filename:
            # Try to detect from class/function names
            class_match = re.search(r'class\s+(\w+)', content)
            func_match = re.search(r'def\s+(\w+)', content)
            
            if class_match and ext == '.py':
                # CamelCase to snake_case
                name = class_match.group(1)
                snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
                filename = f"{snake}{ext}"
            elif func_match and func_match.group(1) == 'main' and ext == '.py':
                filename = f"main{ext}"
            else:
                filename = f"code_{i+1}{ext}"
        
        if filename:
            # Clean up filename: strip absolute paths, current dir prefix, and "workspace/" prefix
            filename = filename.replace('\\', '/')
            filename = re.sub(r'^(\./|/|workspace/|/workspace/)', '', filename, flags=re.IGNORECASE)
            # Ensure it's just a relative path now
            filename = os.path.normpath(filename).replace('\\', '/')
            if filename.startswith('../') or filename.startswith('/'):
                 filename = os.path.basename(filename) # Safety: no traversal

        # Don't overwrite if file already exists and has more content
        filepath = workspace_path / filename
        if filepath.exists():
            existing_size = filepath.stat().st_size
            if existing_size > 0 and existing_size >= len(content):
                continue  # Skip - existing file is larger or equal
        
        # Save the file
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding='utf-8')
            saved_files.append(filename)
        except Exception as e:
            agent_logger.log("System", f"Failed to auto-save {filename}: {e}", "error")
    
    return saved_files

def run_agents(message: str):
    """
    Run CrewAI agents in background.
    """
    try:
        agent_logger.log("System", f"Starting agents with message: {message}", "info")
        
        # Check for API Key (Simple check for demo purposes)
        import os
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("CREWAI_API_KEY") and not os.getenv("GOOGLE_API_KEY") and not os.getenv("ZHIPUAI_API_KEY"):
            # Mock execution if no key is found to demonstrate UI
            agent_logger.log("System", "Note: No API Key found in environment. Running in Demo Mode.", "warning")
            asyncio.run(mock_agent_execution(message))
            return

        # Create agents
        agents = create_agents()
        
        # Custom callback for steps
        def step_callback(step_output):
            thought = getattr(step_output, 'thought', '')
            result = getattr(step_output, 'result', '')
            
            if thought:
                agent_logger.log("Agent", f"Thinking: {thought}", "thought")
            if result:
                agent_logger.log("Agent", f"Action: {result}", "info")
            if not thought and not result:
                agent_logger.log("Agent", f"Working... {str(step_output)}", "info")

        # Task callback - fires when each task completes
        def make_task_callback(task_name):
            def task_callback(output):
                agent_logger.log(task_name, f"Task completed: {str(output)}", "success")
                
                # Post-process Coder output: extract code blocks and save to workspace
                if task_name == "Coder":
                    workspace_path = Path(__file__).resolve().parent / "workspace"
                    saved = extract_and_save_code_blocks(str(output), workspace_path)
                    if saved:
                        agent_logger.log("System", 
                            f"Auto-saved {len(saved)} file(s) from Coder output: {', '.join(saved)}", 
                            "success")
                    else:
                        agent_logger.log("System", 
                            "Note: No new files auto-saved (files may already exist from Tool usage).", 
                            "info")
            return task_callback

        # Define Agents
        architect = agents["architect"]
        coder = agents["coder"]
        tester = agents["tester"]

        # Define Tasks
        # 1. Architect: Design the solution
        agent_logger.log("Architect", "Starting design phase...", "info")
        design_task = Task(
            description=(
                f"ユーザーの要望: '{message}'\n\n"
                "この要望を満たすために必要なファイル構成と実装方針を設計してください。\n\n"
                "【重要】シンプルさを最優先すること。\n"
                "- シンプルな要望には1〜2ファイルで十分です。過剰な設計は不要です。\n"
                "- config.py, utils.py, tests/ などは本当に必要な場合のみ含めてください。\n"
                "- 「シンプルなコード」と言われたら、1ファイルで完結させてください。\n\n"
                "出力には以下を含めてください：\n"
                "- 作成すべきファイル名の一覧\n"
                "- 各ファイルの役割と概要"
            ),
            expected_output="ファイル構成と実装詳細を含む簡潔な設計書",
            agent=architect,
            callback=make_task_callback("Architect")
        )

        # 2. Coder: Implement the code
        agent_logger.log("System", "Starting coding phase...", "info")
        coding_task = Task(
            description=(
                "アーキテクトの設計に基づいて、実際に動作するコードを実装してください。\n\n"
                "【絶対に守るルール】\n"
                "コードは必ず File Writer Tool を使ってファイルに保存してください。\n"
                "チャットにコードを貼り付けるだけでは不十分です。\n\n"
                "【手順】\n"
                "1. 設計書を確認する\n"
                "2. 各ファイルのコードを作成する\n"
                "3. File Writer Tool で各ファイルを保存する（filename, content, overwrite='true' を指定）\n"
                "4. 最終出力に、保存したファイル名の一覧を記載する\n\n"
                "【出力例】\n"
                "以下のファイルをワークスペースに保存しました：\n"
                "- example.py: メインプログラム\n"
                "- utils.py: ユーティリティ関数"
            ),
            expected_output="File Writer Toolで保存したファイル名一覧と実装内容の要約",
            agent=coder,
            context=[design_task],
            callback=make_task_callback("Coder")
        )

        # 3. Tester: Review the code
        agent_logger.log("System", "Starting testing phase...", "info")
        testing_task = Task(
            description=(
                "コーダーが作成したコードをレビューしてください。\n\n"
                "【手順】\n"
                "1. File Reader Tool でワークスペース内のファイルを読み込む\n"
                "2. コードの論理的な誤り、セキュリティの問題、改善点を確認する\n"
                "3. レビュー結果を出力する"
            ),
            expected_output="コードレビューレポートと改善提案",
            agent=tester,
            context=[coding_task],
            callback=make_task_callback("Tester")
        )

        # Create Crew
        crew = Crew(
            agents=[architect, coder, tester],
            tasks=[design_task, coding_task, testing_task],
            process=Process.sequential,
            verbose=True,
            step_callback=step_callback,
            memory=False
        )
        
        agent_logger.log("System", "Crew assembling...", "info")
        result = crew.kickoff()
        agent_logger.log("System", f"Workflow complete!", "success")
        agent_logger.log("Final Output", str(result), "success")
        
        # List workspace files as summary
        workspace_path = (Path(__file__).resolve().parent / "workspace")
        if workspace_path.exists():
            ws_files = [f.name for f in workspace_path.iterdir() if f.is_file() and f.stat().st_size > 0]
            if ws_files:
                agent_logger.log("System", f"Workspace files: {', '.join(ws_files)}", "info")
        
        # Send first Python code block to editor (from any task output)
        result_str = str(result)
        code_match = re.search(r'```python\n(.*?)```', result_str, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            agent_logger.log("System", code, "code")
            agent_logger.log("System", "Code extracted and sent to editor.", "success")
        
    except Exception as e:
        import traceback
        agent_logger.log("System", f"Error during execution: {str(e)}\n{traceback.format_exc()}", "error")

async def mock_agent_execution(message: str):
    """
    Simulate agent activity for demo purposes.
    """
    import time
    time.sleep(1)
    agent_logger.log("Architect", f"Analyzing request: '{message}'", "thought")
    time.sleep(2)
    agent_logger.log("Architect", "Identifying necessary components...", "thought")
    time.sleep(2)
    agent_logger.log("Architect", "Drafting architecture diagram...", "thought")
    time.sleep(2)
    agent_logger.log("Architect", "Decision: Use Python/FastAPI for backend.", "info")
    time.sleep(1)
    agent_logger.log("Architect", "Decision: Use React for frontend.", "info")
    time.sleep(1)
    agent_logger.log("System", "All tasks completed (Demo).", "success")

@app.post("/api/chat")
def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    # Start agent execution in background
    background_tasks.add_task(run_agents, request.message)
    return {"response": "Agents started working on your request."}

@app.get("/api/activity")
def get_activity(after: str = None):
    return {"logs": agent_logger.get_logs(after)}

class RunRequest(BaseModel):
    code: str
    input: str = ""  # Optional input string

@app.post("/api/reset_logs")
async def reset_logs():
    """Clear all agent activity logs."""
    agent_logger.clear()
    return {"status": "success", "message": "Logs cleared"}

@app.post("/api/run")
def run_code(request: RunRequest):
    """
    Execute Python code and return output.
    WARNING: This is unsafe and should be sandboxed in production.
    """
    import sys
    from io import StringIO
    import contextlib

    code = request.code
    input_str = request.input
    output_buffer = StringIO()

    # Get absolute path to workspace
    workspace_path = (Path(__file__).resolve().parent / "workspace").resolve()
    str_workspace_path = str(workspace_path)

    try:
        # Redirect stdout to capture print statements
        # Redirect stdin to provide input
        with contextlib.redirect_stdout(output_buffer):
            # Prepare stdin
            sys.stdin = StringIO(input_str)
            
            # Add workspace to sys.path if not present
            path_added = False
            if str_workspace_path not in sys.path:
                sys.path.insert(0, str_workspace_path)
                path_added = True
            
            try:
                # Execute the code
                exec(code, {'__name__': '__main__'})
            finally:
                # Remove workspace from sys.path if we added it
                if path_added and str_workspace_path in sys.path:
                    sys.path.remove(str_workspace_path)
                # Reset stdin
                sys.stdin = sys.__stdin__
        
        result = output_buffer.getvalue()
        return {"status": "success", "output": result}
        
    except Exception as e:
        # Reset stdin in case of error
        sys.stdin = sys.__stdin__
        return {"status": "error", "output": str(e)}

@app.get("/api/files")
def list_files():
    """List all files in the workspace."""
    workspace_path = Path(".") / "workspace"
    files = []
    if workspace_path.exists():
        for file_path in workspace_path.iterdir():
            if file_path.is_file():
                files.append(file_path.name)
    return {"files": files}

@app.get("/api/files/{filename}")
def read_file(filename: str):
    """Read a specific file from the workspace."""
    safe_filename = Path(filename).name # Prevent directory traversal
    file_path = Path(".") / "workspace" / safe_filename
    if not file_path.exists():
        return {"error": "File not found"}
    try:
        content = file_path.read_text(encoding="utf-8")
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    """Delete a specific file from the workspace."""
    safe_filename = Path(filename).name # Prevent directory traversal
    file_path = Path(".") / "workspace" / safe_filename
    if not file_path.exists():
        return {"error": "File not found"}
    try:
        file_path.unlink()
        return {"status": "success", "message": f"Deleted {filename}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "ok"}

from fastapi import WebSocket, WebSocketDisconnect
# Import TerminalManager from the newly created file
# Ensure terminal_manager.py is in the same directory or PYTHONPATH
try:
    from terminal_manager import TerminalManager
except ImportError:
    # Fallback if running from a different context, though safe_tools implies usage of sys.path
    import sys
    sys.path.append(str(Path(__file__).parent))
    from terminal_manager import TerminalManager

@app.websocket("/api/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    manager = TerminalManager()
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.write(data)
    except WebSocketDisconnect:
        await manager.disconnect()
    except Exception as e:
        print(f"WebSocket error: {e}")
        await manager.disconnect()
