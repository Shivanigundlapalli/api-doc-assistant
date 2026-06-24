import os
import shutil
import streamlit as st
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import get_embedding_model, get_google_api_key, get_chroma_directory

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
    Initializes the vector store.
    """
    persist_directory = get_chroma_directory()
    embeddings = get_embeddings()
    
    try:
        if os.path.exists(persist_directory):
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings
            )
            # Test if it's corrupted by getting the count
            try:
                vector_store._collection.count()
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
        
    persist_directory = get_chroma_directory()
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

def get_retriever(vector_store, k=5, fetch_k=10, similarity_threshold=0.60):
    """
    Configures and returns the retriever with MMR and similarity threshold.
    """
    if not vector_store:
        return None
        
    try:
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": k,
                "score_threshold": similarity_threshold
            }
        )
        return retriever
    except Exception as e:
        st.error(f"Failed to configure retriever: {e}")
        return None
