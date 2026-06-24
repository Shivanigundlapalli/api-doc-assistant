import os
from dotenv import load_dotenv

load_dotenv()

def get_google_api_key() -> str:
    """Retrieves the Google API Key. Raises an error if missing."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key or key == "YOUR_GEMINI_KEY_HERE":
        raise ValueError("GOOGLE_API_KEY is not configured properly in the .env file.")
    return key

def get_openai_api_key() -> str | None:
    """Retrieves the OpenAI API Key. Optional backup."""
    return os.getenv("OPENAI_API_KEY")

def get_langsmith_key() -> str | None:
    """Retrieves the LangSmith API Key for tracing."""
    key = os.getenv("LANGCHAIN_API_KEY")
    if not key or key == "YOUR_LANGSMITH_KEY_HERE":
        return None
    return key

def get_chroma_directory() -> str:
    """Retrieves the ChromaDB storage directory, defaulting to 'chroma_db'."""
    return os.getenv("CHROMA_DB_DIR", "chroma_db")

def get_primary_model() -> str:
    """Retrieves the primary Gemini model name."""
    return os.getenv("PRIMARY_GEMINI_MODEL", "gemini-2.5-flash")

def get_fallback_model() -> str:
    """Retrieves the fallback Gemini model name."""
    return os.getenv("FALLBACK_GEMINI_MODEL", "gemini-flash-lite-latest")

def get_embedding_model() -> str:
    """Retrieves the embedding model. Enforces usage of 'models/gemini-embedding-2'."""
    model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-2")
    if model in ["embedding-001", "models/embedding-001", "models/text-embedding-004"]:
        # Override deprecated models
        return "models/gemini-embedding-2"
    return model

def get_ollama_model() -> str:
    """Retrieves the Ollama model name."""
    return os.getenv("OLLAMA_MODEL", "llama3.1")

def use_ollama_fallback() -> bool:
    """Checks if Ollama should be used as a fallback."""
    return os.getenv("USE_OLLAMA_FALLBACK", "false").lower() == "true"
