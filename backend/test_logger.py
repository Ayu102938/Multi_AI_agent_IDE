from logger import AgentLogger
import time

def test_logger():
    logger = AgentLogger()
    
    logger.log("Architect", "Thinking about design...", "thought")
    assert len(logger.get_logs()) == 1
    assert logger.get_logs()[0]["role"] == "Architect"
    
    # Test timestamp filtering
    first_log_time = logger.get_logs()[0]["timestamp"]
    time.sleep(0.1) 
    logger.log("Coder", "Writing code...", "info")
    
    new_logs = logger.get_logs(after_timestamp=first_log_time)
    assert len(new_logs) == 1
    assert new_logs[0]["role"] == "Coder"
