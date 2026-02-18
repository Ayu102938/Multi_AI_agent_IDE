
@app.post("/api/reset_logs")
async def reset_logs():
    """Clear all agent activity logs."""
    agent_logger.clear()
    return {"status": "success", "message": "Logs cleared"}
