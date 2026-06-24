import streamlit as st
import os

def validate_environment():
    """
    Validates that all required packages and environment settings are in place 
    to prevent unhandled crashes.
    """
    # 1. Validate Dependencies
    required_packages = [
        ("langchain", "langchain"),
        ("langchain_google_genai", "langchain-google-genai"),
        ("langchain_chroma", "langchain-chroma"),
        ("chromadb", "chromadb"),
        ("fpdf", "fpdf2"),
        ("dotenv", "python-dotenv")
    ]
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
            
    if missing:
        st.error(f"Missing required packages: {', '.join(missing)}")
        st.info(f"Please run: pip install -U {' '.join(missing)}")
        st.stop()

    # 2. Validate essential API keys via config
    # We defer this to the actual service initialization to avoid blocking the app 
    # from loading completely. But we can ensure .env file is present.
    if not os.path.exists(".env"):
        st.warning("No `.env` file found. Using default environment variables, which may not be fully configured.")
