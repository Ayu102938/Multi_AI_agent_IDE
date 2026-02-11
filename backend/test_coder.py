from unittest.mock import patch
from agents import create_agents

def test_coder_agent():
    with patch('agents.Agent') as MockAgent:
        agents = create_agents()
        coder = agents["coder"]
        
        assert coder is not None
        
        calls = MockAgent.call_args_list
        coder_call = next((call for call in calls if call.kwargs.get('role') == "Coder"), None)
        
        assert coder_call is not None
        assert "コードを書く" in coder_call.kwargs['goal']
        assert "ポリグロットプログラマー" in coder_call.kwargs['backstory']
