from crewai import Agent
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import FileReadTool, FileWriterTool

# Define workspace path (ensure it matches main.py)
workspace_path = os.path.abspath("workspace")

# Instantiate tools with restricted access
file_read_tool = FileReadTool(base_folder=workspace_path)
file_write_tool = FileWriterTool(base_folder=workspace_path)

def create_agents():
    # Helper to create LLM
    llm = None
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        # Use LiteLLM string format to bypass OpenAI dependency issues in CrewAI
        # and ensuring correct model mapping.
        llm = "gemini/gemini-flash-latest"
        
    elif os.getenv("OPENAI_API_KEY"):
        # CrewAI default, but explicit if needed
        pass
    
    # Common config (Explicitly disable memory to prevent OpenAI dependency)
    agent_config = {"llm": llm, "memory": False} if llm else {}

    return {
        "architect": Agent(
            role="Architect", 
            goal="ユーザーの要望を技術的なタスク（DB設計、API実装、UI実装など）に分解し、ファイル構成を設計する。", 
            backstory="あなたは熟練したソフトウェアアーキテクトです。ユーザーの曖昧な要望を明確な技術仕様とタスクに変換する責任があります。FileReadToolを使用してワークスペース内のファイルを確認できます。",
            tools=[file_read_tool, file_write_tool],
            **agent_config
        ),
        "coder": Agent(
            role="Coder", 
            goal="与えられた技術的タスクに基づいて実行可能なコードを書き、ワークスペースにファイルとして保存する。", 
            backstory="あなたは様々なプログラミング言語に精通したポリグロットプログラマーです。アーキテクトの設計に従い、高品質なコードを実装します。**必ずFileWriterToolを使用して、コードをワークスペース内の適切なファイルに保存してください。**",
            tools=[file_read_tool, file_write_tool],
            **agent_config
        ),
        "critic": Agent(
            role="Critic",
            goal="コードの品質、セキュリティ、ベストプラクティスをレビューする",
            backstory="あなたは厳格なコードレビュアーです。セキュリティの脆弱性や非効率なコードを見逃さず、常に改善案を提示します。",
            **agent_config
        ),
        "tester": Agent(
            role="Tester",
            goal="生成されたコードの単体テストを作成し、実行して動作を保証する。テストコードもファイルとして保存する。",
            backstory="あなたは品質保証のスペシャリストです。あらゆるエッジケースを想定したテストケースを作成し、コードの堅牢性を担保します。FileReadToolでコードを読み、FileWriterToolでテストを作成してください。",
            tools=[file_read_tool, file_write_tool],
            **agent_config
        ),
        "librarian": Agent(
            role="Librarian",
            goal="プロジェクトのドキュメントを整備し、常に最新の状態に保つ。README.mdなどを更新する。",
            backstory="あなたは几帳面なドキュメント管理者です。READMEやAPIドキュメントが、実際のコードと乖離しないように監視・更新します。FileWriterToolを使用してドキュメントを更新してください。",
            tools=[file_read_tool, file_write_tool],
            **agent_config
        )
    }
