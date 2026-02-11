from unittest.mock import patch
from agents import create_agents

def test_remaining_agents():
    with patch('agents.Agent') as MockAgent:
        agents = create_agents()
        
        # Verify Critic
        critic = agents["critic"]
        assert critic is not None
        critic_call = next((call for call in MockAgent.call_args_list if call.kwargs.get('role') == "Critic"), None)
        assert critic_call is not None
        assert "レビュー" in critic_call.kwargs['goal']

        # Verify Tester
        tester = agents["tester"]
        assert tester is not None
        tester_call = next((call for call in MockAgent.call_args_list if call.kwargs.get('role') == "Tester"), None)
        assert tester_call is not None
        assert "テスト" in tester_call.kwargs['goal']

        # Verify Librarian
        librarian = agents["librarian"]
        assert librarian is not None
        librarian_call = next((call for call in MockAgent.call_args_list if call.kwargs.get('role') == "Librarian"), None)
        assert librarian_call is not None
        assert "ドキュメント" in librarian_call.kwargs['goal']
