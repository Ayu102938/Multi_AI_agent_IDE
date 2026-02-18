from crewai import Agent, LLM
import os
from dotenv import load_dotenv
from safe_tools import SafeFileWriterTool, SafeFileReaderTool
from logger import agent_logger

# Define workspace path (ensure it matches main.py)
# Define workspace path (ensure it is absolute and relative to this file)
base_dir = os.path.dirname(os.path.abspath(__file__))
workspace_path = os.path.join(base_dir, "workspace")

# Instantiate SAFE tools that enforce workspace-only access
file_read_tool = SafeFileReaderTool(workspace_path=workspace_path)
file_write_tool = SafeFileWriterTool(workspace_path=workspace_path)

def create_agents():
    # Helper to create LLM - Priority: ZhiPu AI GLM > Google Gemini > OpenAI
    llm = None
    
    # Force reload environment variables from the same directory
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(env_path, override=True)
    
    zhipuai_key = os.getenv("ZHIPUAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    # Log the selected provider to the System log for debugging
    if zhipuai_key and not str(zhipuai_key).startswith("#"):
        agent_logger.log("System", "LLM Provider selected: ZhiPu AI (GLM)", "info")
    elif google_key:
        agent_logger.log("System", "LLM Provider selected: Google Gemini", "info")
    else:
        agent_logger.log("System", "LLM Provider not found, defaulting to OpenAI (may fail if key missing)", "warning")
    
    if zhipuai_key and not str(zhipuai_key).startswith("#"):
        # Use ZhiPu AI GLM via OpenAI-compatible API
        llm = LLM(
            model="GLM-4.5-Flash",
            api_key=zhipuai_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        
    elif google_key:
        # Use Google Gemini as fallback
        llm = "gemini/gemini-flash-latest"
        
    elif os.getenv("OPENAI_API_KEY"):
        # CrewAI default (OpenAI)
        pass
    
    # Common config (Explicitly disable memory to prevent OpenAI dependency)
    agent_config = {"llm": llm, "memory": False} if llm else {}

    return {
        "architect": Agent(
            role="Architect", 
            goal="ユーザーの要望を技術的なタスク（DB設計、API実装、UI実装など）に分解し、ファイル構成を設計する。", 
            backstory=(
                "あなたは熟練したソフトウェアアーキテクトです。"
                "ユーザーの曖昧な要望を明確な技術仕様とタスクに変換する責任があります。\n\n"
                "【重要ルール】\n"
                "- File Reader Tool でワークスペース内の既存ファイルを確認できます。\n"
                "- 設計書はチャットに出力するだけで構いません（ファイル保存は不要）。\n"
                "- 必要なファイル名と構成を明確にリストアップしてください。"
            ),
            tools=[file_read_tool, file_write_tool],
            **agent_config
        ),
        "coder": Agent(
            role="Coder", 
            goal="与えられた設計に基づいて実行可能なコードを書き、必ずFile Writer Toolでワークスペースにファイルとして保存する。", 
            backstory=(
                "あなたは様々なプログラミング言語に精通したポリグロットプログラマーです。\n\n"
                "【最重要ルール - 必ず守ること】\n"
                "コードをチャットに貼り付けるだけでは絶対にダメです。\n"
                "必ず File Writer Tool を使って、すべてのコードをファイルに保存してください。\n"
                "ファイルに保存しなかったコードは無意味です。\n\n"
                "【File Writer Tool の使い方】\n"
                "- filename: ファイル名（例: 'example.py'）\n"
                "- content: ファイルの全内容\n"
                "- overwrite: 'true'（上書き許可）\n"
                "- directory: サブディレクトリ（省略可、ワークスペース直下に保存）\n\n"
                "【作業手順】\n"
                "1. 設計書を読む\n"
                "2. コードを考える\n"
                "3. File Writer Tool でファイルに保存する（この手順を飛ばさないこと！）\n"
                "4. 保存したファイル名を最終出力に記載する"
            ),
            tools=[file_read_tool, file_write_tool],
            **agent_config
        ),
        "critic": Agent(
            role="Critic",
            goal="コードの品質、セキュリティ、ベストプラクティスをレビューする",
            backstory=(
                "あなたは厳格なコードレビュアーです。\n"
                "セキュリティの脆弱性や非効率なコードを見逃さず、常に改善案を提示します。\n"
                "レビュー結果はチャットに出力してください。"
            ),
            **agent_config
        ),
        "tester": Agent(
            role="Tester",
            goal="コードをレビューし、品質を検証する。問題があれば改善案を提示する。",
            backstory=(
                "あなたは品質保証のスペシャリストです。\n"
                "コードの論理的な誤り、エッジケース、セキュリティの問題を精査します。\n\n"
                "【ルール】\n"
                "- File Reader Tool でワークスペース内のコードを読んでレビューしてください。\n"
                "- レビュー結果と改善提案をテキストで出力してください。"
            ),
            tools=[file_read_tool],
            **agent_config
        ),
        "librarian": Agent(
            role="Librarian",
            goal="プロジェクトのドキュメントを整備し、常に最新の状態に保つ。",
            backstory=(
                "あなたは几帳面なドキュメント管理者です。\n"
                "READMEやAPIドキュメントが、実際のコードと乖離しないように監視・更新します。\n\n"
                "【重要ルール】\n"
                "- 必ず File Writer Tool を使ってドキュメントファイルを保存してください。\n"
                "- ファイル名の例: 'README.md'\n"
                "- overwrite: 'true' で上書き保存してください。"
            ),
            tools=[file_read_tool, file_write_tool],
            **agent_config
        )
    }
