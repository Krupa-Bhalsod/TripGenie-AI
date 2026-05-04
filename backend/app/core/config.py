import os
from dotenv import load_dotenv

# Try to load .env from the root directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
load_dotenv(dotenv_path)
load_dotenv() # Also try current directory just in case


class Settings:
    def __init__(self):
        self.APP_NAME = "TripGenie AI"

        # Database
        self.SQLITE_URL = os.getenv("SQLITE_URL", "sqlite:///./db.sqlite")

        # LLM Settings
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") # groq, gemini, openai, ollama
        self.LLM_MODEL = os.getenv("LLM_MODEL") # If set, overrides provider-specific defaults
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", 0.6))

        # Groq
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # Google Gemini
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Ollama
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5")

        # Anthropic
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

        # Tavily
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

        # Embeddings
        self.EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./vector_store/faiss_index")
        # JWT
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_dev_secret")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
        )

settings = Settings()