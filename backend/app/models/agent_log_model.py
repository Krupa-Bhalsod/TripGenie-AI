from pydantic import BaseModel
from typing import Dict, Any


class AgentLog(BaseModel):
    agent_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    execution_time_ms: int