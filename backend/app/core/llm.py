"""
LLM configuration — Support for Groq, Google Gemini, and OpenAI.
"""
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent
from app.core.config import settings

def get_llm():
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "groq":
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL or settings.GROQ_MODEL,
            temperature=settings.TEMPERATURE
        )
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.LLM_MODEL or settings.GEMINI_MODEL,
            temperature=settings.TEMPERATURE
        )
    elif provider == "openai":
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.LLM_MODEL or settings.OPENAI_MODEL,
            temperature=settings.TEMPERATURE
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            model=settings.LLM_MODEL or settings.ANTHROPIC_MODEL,
            temperature=settings.TEMPERATURE,
        )
    elif provider == "ollama":
        return ChatOllama(
            model=settings.LLM_MODEL or settings.OLLAMA_MODEL,
            temperature=settings.TEMPERATURE,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

# Initialize the LLM based on settings
llm = get_llm()


def create_agent(system_prompt: str, tools: list = None, **kwargs):
    """Create a deepagent with the configured LLM model."""
    if tools is None:
        tools = []
    return create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        **kwargs
    )