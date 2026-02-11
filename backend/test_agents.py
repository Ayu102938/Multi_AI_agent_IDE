from unittest.mock import patch
from agents import create_agents

def test_agents_creation():
    with patch('agents.Agent') as MockAgent:
        agents = create_agents()
        assert "architect" in agents
        assert "coder" in agents
