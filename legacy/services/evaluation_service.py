import os
from config import get_langsmith_key

def initialize_langsmith():
    """
    Initializes LangSmith tracing if configuration is present.
    """
    api_key = get_langsmith_key()
    tracing_enabled = os.environ.get("LANGCHAIN_TRACING_V2") == "true"
    
    if api_key and tracing_enabled:
        print("LangSmith tracing is ENABLED.")
        return True
    else:
        print("LangSmith tracing is DISABLED. Configure LANGCHAIN_API_KEY to enable.")
        return False
