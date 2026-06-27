import streamlit as st
from services.logging.logger import get_logger
from services.error_handler.handler import PipelineError

logger = get_logger("RetrieverManager")

@st.cache_resource(show_spinner=False)
def get_retriever(_vector_store, k=8):
    if not _vector_store:
        raise PipelineError("Retriever", "Cannot initialize retriever without a valid vector database.")
        
    try:
        # 1. Vector Retriever (MMR)
        vector_retriever = _vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": 20,
                "lambda_mult": 0.5
            }
        )
        
        # 2. BM25 Keyword Retriever
        from langchain_community.retrievers import BM25Retriever
        from langchain.schema import Document
        from langchain.retrievers import EnsembleRetriever
        
        docs_data = _vector_store.get()
        texts = docs_data.get('documents', [])
        metadatas = docs_data.get('metadatas', [])
        
        documents = [Document(page_content=t, metadata=m or {}) for t, m in zip(texts, metadatas)]
        
        if documents:
            bm25_retriever = BM25Retriever.from_documents(documents)
            bm25_retriever.k = k
            
            # 3. Ensemble Retriever (50% Semantic, 50% Keyword)
            ensemble_retriever = EnsembleRetriever(
                retrievers=[vector_retriever, bm25_retriever],
                weights=[0.5, 0.5]
            )
            return ensemble_retriever
            
        return vector_retriever
        
    except Exception as e:
        logger.error(f"Retriever init failed: {e}")
        raise PipelineError("Retriever", "Failed to configure the documentation retriever.")

def retrieve_chunks(retriever, query: str, top_k: int = 10):
    if not retriever:
        raise PipelineError("Retriever", "Retriever is not initialized.")
    try:
        raw_docs = retriever.invoke(query)
        logger.info(f"Retrieved {len(raw_docs)} chunks.")
        return raw_docs[:top_k]
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise PipelineError("Retriever", "Failed to retrieve documents.")
