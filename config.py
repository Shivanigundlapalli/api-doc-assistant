import os
import streamlit as st
from dotenv import load_dotenv

# Ensure local .env is loaded into os.environ
load_dotenv()

def get_config(key: str, default: str = None) -> str:
    """Safely retrieves a configuration key, prioritizing Streamlit Secrets over environment variables."""
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    
    return os.getenv(key, default)

def get_google_api_key() -> str:
    """Retrieves the Google API Key. Raises an error if missing."""
    key = get_config("GOOGLE_API_KEY")
    if not key or key == "YOUR_GEMINI_KEY_HERE":
        raise ValueError("GOOGLE_API_KEY is not configured in Streamlit Secrets or .env.")
    return key

def get_openai_api_key() -> str | None:
    """Retrieves the OpenAI API Key. Optional backup."""
    return get_config("OPENAI_API_KEY")

def get_langsmith_key() -> str | None:
    """Retrieves the LangSmith API Key for tracing."""
    key = get_config("LANGCHAIN_API_KEY")
    if not key or key == "YOUR_LANGSMITH_KEY_HERE":
        return None
    return key

def get_chroma_directory() -> str:
    """Retrieves the ChromaDB storage directory, defaulting to 'chroma_db'."""
    return get_config("CHROMA_DB_DIR", "chroma_db")

def get_primary_model() -> str:
    """Retrieves the primary Gemini model name."""
    return get_config("PRIMARY_GEMINI_MODEL", "gemini-2.5-flash")

def get_fallback_model() -> str:
    """Retrieves the fallback Gemini model name."""
    return get_config("FALLBACK_GEMINI_MODEL", "gemini-flash-lite-latest")

def get_embedding_model() -> str:
    """Retrieves the embedding model. Enforces usage of 'models/gemini-embedding-2'."""
    model = get_config("EMBEDDING_MODEL", "models/gemini-embedding-2")
    if model in ["embedding-001", "models/embedding-001", "models/text-embedding-004"]:
        # Override deprecated models
        return "models/gemini-embedding-2"
    return model

def get_ollama_model() -> str:
    """Retrieves the Ollama model name."""
    return get_config("OLLAMA_MODEL", "llama3.1")

def use_ollama_fallback() -> bool:
    """Checks if Ollama should be used as a fallback."""
    return get_config("USE_OLLAMA_FALLBACK", "false").lower() == "true"
