import os
from dotenv import load_dotenv

# Try to load .env from the root directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
load_dotenv(dotenv_path)
load_dotenv() # Also try current directory just in case


class Settings:
    def __init__(self):
        self.APP_NAME = "TripGenie AI"

        # Mongo
        self.MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME", "tripgenie")

        # Groq
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

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