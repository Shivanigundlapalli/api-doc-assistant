from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.domain import User
from services.rag_service import rag_service, RAGQuery
import uuid

router = APIRouter()

# Mocking the dependency for Phase 3 UI Testing without forcing a full login
async def get_mock_user() -> User:
    return User(id=uuid.uuid4(), org_id=uuid.uuid4(), email="test@enterprise.com", role="admin")

@router.post("/completions")
async def chat_completions(
    query_data: dict,
    current_user: User = Depends(get_mock_user)
):
    """
    Enterprise Chat API Endpoint.
    Receives user query, enforces Tenant ID isolation, and returns Server-Sent Events (SSE).
    """
    if "query" not in query_data:
        raise HTTPException(status_code=400, detail="Missing 'query' field.")
        
    rag_query = RAGQuery(
        query=query_data["query"],
        org_id=str(current_user.org_id), # Enforced Multi-Tenancy
        chat_history=query_data.get("history", [])
    )
    
    # Return StreamingResponse for SSE
    return StreamingResponse(
        rag_service.generate_streaming_answer(rag_query), 
        media_type="text/event-stream"
    )
