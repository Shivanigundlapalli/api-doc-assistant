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
from tenacity import retry, stop_after_attempt, wait_exponential

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
    google_key = get_google_api_key()
    openai_key = get_config("OPENAI_API_KEY")
    
    # 1. Try Gemini
    if google_key and google_key != "YOUR_GEMINI_KEY_HERE":
        try:
            model = get_embedding_model()
            embeddings = GoogleGenerativeAIEmbeddings(model=model, google_api_key=google_key)
            # Test key immediately to catch 400/403 errors
            embeddings.embed_query("test")
            log_stage("Embeddings", "Initialized Gemini")
            return embeddings
        except Exception as e:
            logger.warning(f"Gemini embeddings failed (invalid key or unsupported region): {e}. Falling back to OpenAI.")
            
    # 2. Try OpenAI
    if openai_key and openai_key != "YOUR_OPENAI_KEY_HERE":
        try:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai_key)
            embeddings.embed_query("test")
            log_stage("Embeddings", "Initialized OpenAI Fallback")
            return embeddings
        except Exception as e:
            logger.warning(f"OpenAI embeddings failed: {e}")
            
    raise PipelineError("VectorDB", "Failed to connect to any embedding model. Please check that your API keys are correct.")

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
            # We no longer wipe the directory because it breaks Chroma's in-memory lock
            # and leads to infinite appending. Instead, we let Chroma handle it,
            # and we will use deterministic IDs when adding documents.
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
        persist_directory.mkdir(parents=True, exist_ok=True)
        
        embeddings = get_embeddings()
        
        # Deduplicate chunks to prevent Chroma ValueError (Expected IDs to be unique)
        unique_chunks = []
        ids = []
        seen = set()
        
        for chunk in chunks:
            # Hash both content and metadata to be safe
            chunk_hash = hashlib.md5((chunk.page_content + str(chunk.metadata)).encode('utf-8')).hexdigest()
            if chunk_hash not in seen:
                seen.add(chunk_hash)
                unique_chunks.append(chunk)
                ids.append(chunk_hash)
        
        @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=20))
        def _safe_embed():
            return Chroma.from_documents(
                documents=unique_chunks,
                embedding=embeddings,
                persist_directory=str(persist_directory),
                ids=ids
            )
            
        vector_store = _safe_embed()
        
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
