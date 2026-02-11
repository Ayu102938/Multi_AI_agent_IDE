from datetime import datetime
from typing import List, Dict, Any

class AgentLogger:
    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def log(self, agent_role: str, message: str, message_type: str = "info"):
        """
        Log an event from an agent.
        message_type: 'info', 'thought', 'command', 'error'
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": agent_role,
            "message": message,
            "type": message_type
        }
        self._logs.append(entry)
        # Keep only recent logs to avoid memory issues if strictly needed, 
        # but for now let's keep all for the session.

    def get_logs(self, after_timestamp: str = None) -> List[Dict[str, Any]]:
        """
        Get logs, optionally filtering by timestamp to get only new ones.
        """
        if not after_timestamp:
            return self._logs
        
        return [log for log in self._logs if log["timestamp"] > after_timestamp]

    def clear(self):
        self._logs = []

# Global instance
agent_logger = AgentLogger()
