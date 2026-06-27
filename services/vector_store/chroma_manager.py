import os
import shutil
import hashlib
import json
from pathlib import Path
import streamlit as st
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import get_embedding_model, get_google_api_key, get_chroma_directory
from services.logging.logger import get_logger, log_stage
from services.error_handler.handler import PipelineError

logger = get_logger("ChromaManager")

def _get_persist_directory() -> Path:
    base_dir = Path(__file__).parent.parent.parent.absolute()
    return base_dir / get_chroma_directory()

def get_directory_checksum(directory_path: str) -> str:
    """Computes a checksum based on file contents in the docs directory."""
    hasher = hashlib.md5()
    for root, _, files in os.walk(directory_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            hasher.update(file.encode())
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
    return hasher.hexdigest()

@st.cache_resource(show_spinner=False)
def get_embeddings():
    api_key = get_google_api_key()
    if not api_key:
        logger.error("Missing Google API key for embeddings.")
        raise PipelineError("VectorDB", "Configuration missing. Please set your GOOGLE_API_KEY.")
        
    model = get_embedding_model()
    embeddings = GoogleGenerativeAIEmbeddings(
        model=model, 
        google_api_key=api_key
    )
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            embeddings.embed_query("test")
            log_stage("Embeddings", "Initialized")
            return embeddings
        except Exception as e:
            logger.error(f"Embedding initialization attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise PipelineError("VectorDB", f"Failed to connect to embedding model {model}.")

@st.cache_resource(show_spinner=False)
def initialize_vector_store(docs_dir: str):
    """
    Initializes ChromaDB using checksum validation to prevent infinite rebuilds.
    Returns (vector_store, needs_rebuild)
    """
    persist_directory = _get_persist_directory()
    metadata_file = persist_directory / "metadata.json"
    
    try:
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        current_checksum = get_directory_checksum(docs_dir)
        needs_rebuild = False
        
        if not metadata_file.exists():
            needs_rebuild = True
            logger.info("Metadata missing. Forcing rebuild.")
        else:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            if metadata.get("checksum") != current_checksum:
                needs_rebuild = True
                logger.info("Checksum mismatch. Forcing rebuild.")
            
        sqlite_file = persist_directory / "chroma.sqlite3"
        if not sqlite_file.exists():
            needs_rebuild = True
            
        if needs_rebuild:
            # Wipe corrupted/outdated directory if exists
            if persist_directory.exists():
                shutil.rmtree(persist_directory)
                persist_directory.mkdir(parents=True, exist_ok=True)
            return None, True
            
        embeddings = get_embeddings()
        vector_store = Chroma(
            persist_directory=str(persist_directory),
            embedding_function=embeddings
        )
        
        try:
            count = vector_store._collection.count()
            if count == 0:
                return None, True
        except Exception as e:
            logger.warning(f"Corrupted collection: {e}")
            return None, True
            
        return vector_store, False
        
    except Exception as e:
        logger.error(f"Initialize DB failed: {e}")
        if persist_directory.exists():
            shutil.rmtree(persist_directory)
        return None, True

def build_vector_store(chunks: list, docs_dir: str):
    if not chunks or len(chunks) == 0:
        raise PipelineError("VectorDB", "No document chunks available.")
        
    persist_directory = _get_persist_directory()
    try:
        # Strictly wipe the directory before building a new collection
        if persist_directory.exists():
            shutil.rmtree(persist_directory)
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        embeddings = get_embeddings()
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(persist_directory)
        )
        
        # Write metadata
        current_checksum = get_directory_checksum(docs_dir)
        metadata = {
            "checksum": current_checksum,
            "chunk_count": len(chunks),
            "model": get_embedding_model()
        }
        with open(persist_directory / "metadata.json", "w") as f:
            json.dump(metadata, f)
            
        log_stage("VectorDB", "Built successfully", {"chunks": len(chunks)})
        return vector_store
        
    except Exception as e:
        raise PipelineError("VectorDB", f"Failed to build vector DB: {e}")
