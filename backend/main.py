from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel

from fastapi import BackgroundTasks
from logger import agent_logger
import asyncio
from agents import create_agents
from crewai import Crew, Process, Task

class ChatRequest(BaseModel):
    message: str

def run_agents(message: str):
    """
    Run CrewAI agents in background.
    """
    try:
        agent_logger.log("System", f"Starting agents with message: {message}", "info")
        
        # Check for API Key (Simple check for demo purposes)
        import os
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("CREWAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            # Mock execution if no key is found to demonstrate UI
            agent_logger.log("System", "Note: No API Key found in environment. Running in Demo Mode.", "warning")
            asyncio.run(mock_agent_execution(message))
            return

        # Create agents
        agents = create_agents()
        
        # Custom callback for steps
        def step_callback(step_output):
            # step_output is a valid CrewAI step object
            # We try to extract thought/result
            # Note: CrewAI step objects might vary by version, robust check:
            thought = getattr(step_output, 'thought', '')
            result = getattr(step_output, 'result', '')
            
            if thought:
                agent_logger.log("Agent", f"Thinking: {thought}", "thought")
            if result:
                agent_logger.log("Agent", f"Action: {result}", "info")
            if not thought and not result:
                agent_logger.log("Agent", f"Working... {str(step_output)[:100]}", "info")

        # Define Agents
        architect = agents["architect"]
        coder = agents["coder"]
        tester = agents["tester"]

        # Define Tasks
        # 1. Architect: Design the solution
        design_task = Task(
            description=f"ユーザーの要望: '{message}'\n\nこの要望を満たすアプリケーションのアーキテクチャ、必要なファイル構成、および実装ステップを設計してください。",
            expected_output="ファイル構成と実装詳細を含む設計書",
            agent=architect,
            callback=step_callback
        )

        # 2. Coder: Implement the code
        coding_task = Task(
            description="アーキテクトの設計に基づいて、実際に動作するコードを記述してください。すべての必要なファイル（main.py, requirements.txtなど）の内容を提供してください。",
            expected_output="実装されたソースコード",
            agent=coder,
            context=[design_task],
            callback=step_callback
        )

        # 3. Tester: Verify the code (Mock testing for now as we can't run it yet)
        testing_task = Task(
            description="コーダーが作成したコードをレビューし、論理的な誤りやセキュリティ上の問題がないか確認してください。",
            expected_output="コードレビューレポートと修正案（もしあれば）",
            agent=tester,
            context=[coding_task],
            callback=step_callback
        )

        # Create Crew
        crew = Crew(
            agents=[architect, coder, tester],
            tasks=[design_task, coding_task, testing_task],
            process=Process.sequential,
            verbose=True,
            memory=False # Explicitly disable memory to prevent OpenAI embedding requirement
        )
        
        agent_logger.log("System", "Crew assembling...", "info")
        result = crew.kickoff()
        agent_logger.log("System", f"Workflow complete!", "success")
        agent_logger.log("Final Output", str(result), "success")
        
        # Extract code from result (Naive approach for Python blocks)
        result_str = str(result)
        import re
        code_match = re.search(r'```python\n(.*?)```', result_str, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            agent_logger.log("System", code, "code")
            agent_logger.log("System", "Code extracted and sent to editor.", "success")
        
    except Exception as e:
        agent_logger.log("System", f"Error during execution: {str(e)}", "error")

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
    output_buffer = StringIO()

    try:
        # Redirect stdout to capture print statements
        with contextlib.redirect_stdout(output_buffer):
            # Execute the code
            exec(code, {'__name__': '__main__'})
        
        result = output_buffer.getvalue()
        return {"status": "success", "output": result}
        
    except Exception as e:
        return {"status": "error", "output": str(e)}

@app.get("/")
def read_root():
    return {"status": "ok"}
