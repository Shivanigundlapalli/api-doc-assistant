from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Splits documents into chunks suitable for embedding.
    """
    if not documents:
        return []
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        # Add chunk index and standard metadata
        for i, chunk in enumerate(chunks):
            source = chunk.metadata.get("source", "unknown")
            chunk.metadata["chunk_id"] = f"{source}_chunk_{i}"
            # Ensure only string/int/float types for ChromaDB compatibility
            if chunk.metadata and isinstance(chunk.metadata, dict):
                chunk.metadata = {k: str(v) for k, v in chunk.metadata.items()}
            
        return chunks
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return []

def deduplicate_docs(docs):
    """
    Removes duplicate documents returned by the retriever based on content.
    """
    unique_contents = set()
    deduped = []
    for doc in docs:
        content_hash = hash(doc.page_content)
        if content_hash not in unique_contents:
            unique_contents.add(content_hash)
            deduped.append(doc)
    return deduped

def format_metadata(metadata: dict) -> str:
    """
    Format metadata nicely for UI display.
    """
    source = metadata.get("source", "Unknown")
    filename = source.split("/")[-1].split("\\")[-1]
    return f"📄 {filename}"
