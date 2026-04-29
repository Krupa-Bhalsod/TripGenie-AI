"""
LLM configuration — Local Ollama (qwen2.5).
"""
from langchain_ollama import ChatOllama
from deepagents import create_deep_agent
from app.core.config import settings


# Local Ollama instance
llm = ChatOllama(
    model="qwen2.5",
    temperature=0.0,
)


def create_agent(system_prompt: str, tools: list = None, **kwargs):
    """Create a deepagent with the local Ollama model."""
    if tools is None:
        tools = []
    return create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        **kwargs
    )