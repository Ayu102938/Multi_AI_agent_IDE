from crewai import Agent
import os
from langchain_google_genai import ChatGoogleGenerativeAI

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
            goal="ユーザーの要望を技術的なタスク（DB設計、API実装、UI実装など）に分解する", 
            backstory="あなたは熟練したソフトウェアアーキテクトです。ユーザーの曖昧な要望を明確な技術仕様とタスクに変換する責任があります。",
            **agent_config
        ),
        "coder": Agent(
            role="Coder", 
            goal="与えられた技術的タスクに基づいて実行可能なコードを書く", 
            backstory="あなたは様々なプログラミング言語に精通したポリグロットプログラマーです。アーキテクトの設計に従い、高品質なコードを実装します。",
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
            goal="生成されたコードの単体テストを作成し、実行して動作を保証する",
            backstory="あなたは品質保証のスペシャリストです。あらゆるエッジケースを想定したテストケースを作成し、コードの堅牢性を担保します。",
            **agent_config
        ),
        "librarian": Agent(
            role="Librarian",
            goal="プロジェクトのドキュメントを整備し、常に最新の状態に保つ",
            backstory="あなたは几帳面なドキュメント管理者です。READMEやAPIドキュメントが、実際のコードと乖離しないように監視・更新します。",
            **agent_config
        )
    }
