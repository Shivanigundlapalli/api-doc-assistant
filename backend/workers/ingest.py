import os
import uuid
from celery import Celery

# Celery configured to use the Redis container from our docker-compose
celery_app = Celery(
    "documind_workers",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
)

@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: str, org_id: str, source_url: str):
    """
    Asynchronous ingestion pipeline task.
    Triggered when a user connects a GitHub repo or uploads a PDF.
    """
    try:
        print(f"Starting ingestion for Doc {document_id} (Org: {org_id})")
        
        # 1. Fetch / Crawl
        # raw_text = crawl_website(source_url) OR extract_pdf(source_url)
        raw_text = "# Authentication\nTo login, use the /auth endpoint."
        
        # 2. Semantic Chunking (LangChain)
        # We use RecursiveCharacterTextSplitter with specific separators to keep headers intact.
        # chunks = semantic_chunker.split_text(raw_text)
        chunks = [raw_text]
        
        # 3. Embedding Generation (OpenAI text-embedding-3-small)
        # vectors = openai.embeddings.create(input=chunks, model="text-embedding-3-small")
        vectors = [[0.01, 0.02, 0.03]] # Mock vector
        
        # 4. Vector DB Upsert (Pinecone)
        # CRITICAL: We attach the org_id to EVERY chunk's metadata to enforce isolation.
        upsert_payload = []
        for i, chunk in enumerate(chunks):
            upsert_payload.append({
                "id": f"{document_id}_chunk_{i}",
                "values": vectors[i],
                "metadata": {
                    "org_id": org_id,
                    "document_id": document_id,
                    "text": chunk,
                    "source": source_url
                }
            })
            
        # pinecone_index.upsert(vectors=upsert_payload, namespace=org_id)
        
        # 5. Update Postgres DB Status
        # db.query(Document).filter(id=document_id).update({"sync_status": "completed"})
        
        print(f"Ingestion complete for {document_id}")
        return {"status": "success", "chunks_processed": len(chunks)}
        
    except Exception as exc:
        print(f"Ingestion failed: {exc}")
        self.retry(exc=exc, countdown=60) # Exponential backoff in production
