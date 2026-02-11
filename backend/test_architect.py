from unittest.mock import patch
from agents import create_agents

def test_architect_agent():
    with patch('agents.Agent') as MockAgent:
        agents = create_agents()
        architect = agents["architect"]
        
        # Verify Architect's role and goal
        # Note: MockAgent is called, so we check the warnings or call args if needed, 
        # but here we just check if it exists and has expected keys in the dict
        assert architect is not None
        
        # Verify call arguments
        # The key is "architect", value is the Mock object returned by Agent(...)
        # We want to check if Agent was called with correct arguments
        
        # Find the call for Architect
        # MockAgent.call_args_list contain all calls. 
        # We expect at least one call with role="Architect"
        
        calls = MockAgent.call_args_list
        architect_call = next((call for call in calls if call.kwargs.get('role') == "Architect"), None)
        
        assert architect_call is not None
        assert architect_call.kwargs['goal'] == "ユーザーの要望を技術的なタスク（DB設計、API実装、UI実装など）に分解する"
        assert "リーダー" in architect_call.kwargs['backstory'] or "Architect" in architect_call.kwargs['backstory']
