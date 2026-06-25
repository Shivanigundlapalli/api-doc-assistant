from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from core.security import get_current_active_user
from models.domain import User
from services.rag_service import rag_service, RAGQuery

router = APIRouter()

@router.post("/completions")
async def chat_completions(
    query_data: dict,
    current_user: User = Depends(get_current_active_user)
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
