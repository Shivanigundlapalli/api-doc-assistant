import os
import shutil
import streamlit as st
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import get_embedding_model, get_google_api_key, get_chroma_directory

@st.cache_resource(show_spinner=False)
def get_embeddings():
    try:
        api_key = get_google_api_key()
    except ValueError as e:
        st.error(str(e))
        st.stop()
        
    model = get_embedding_model()
    embeddings = GoogleGenerativeAIEmbeddings(
        model=model, 
        google_api_key=api_key
    )
    try:
        # Test if the embedding model is available
        embeddings.embed_query("test")
    except Exception as e:
        st.error(f"Embedding initialization failed for model {model}: {e}")
        st.stop()
        
    return embeddings

@st.cache_resource(show_spinner=False)
def initialize_vector_store():
    """
    Initializes the vector store. Checks for corruption or empty states (crucial for Cloud deployments).
    """
    # Use absolute paths for Cloud reliability
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persist_directory = os.path.join(base_dir, get_chroma_directory())
    embeddings = get_embeddings()
    
    try:
        if os.path.exists(persist_directory):
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            # Test if it's corrupted OR empty (which happens if Streamlit recreates the directory)
            try:
                count = vector_store._collection.count()
                if count == 0:
                    print("ChromaDB exists but collection is empty. Forcing rebuild.")
                    return None
            except Exception as collection_e:
                print(f"ChromaDB collection corrupted: {collection_e}")
                raise collection_e
            return vector_store
        else:
            return None # Needs to be built
    except Exception as e:
        print(f"Error loading ChromaDB: {e}. Attempting recovery by deleting and rebuilding.")
        # Recovery from corruption
        if os.path.exists(persist_directory):
            try:
                shutil.rmtree(persist_directory)
            except Exception as del_e:
                print(f"Failed to delete corrupted ChromaDB directory: {del_e}")
        return None

def build_vector_store(chunks):
    """
    Builds the vector store from chunks and persists it.
    """
    if not chunks:
        return None
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    persist_directory = os.path.join(base_dir, get_chroma_directory())
    try:
        embeddings = get_embeddings()
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        return vector_store
    except Exception as e:
        st.error(f"Failed to build vector store: {e}")
        return None

def get_retriever(vector_store, k=10):
    """
    Configures and returns the retriever using MMR.
    """
    if not vector_store:
        return None
        
    try:
        # Base Retriever using MMR
        base_retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": 20,
                "lambda_mult": 0.5
            }
        )
        
        return base_retriever
    except Exception as e:
        st.error(f"Failed to configure retriever: {e}")
        return None
