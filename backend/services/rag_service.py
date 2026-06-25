import json
import asyncio
from typing import AsyncGenerator, List, Dict
from pydantic import BaseModel

class RAGQuery(BaseModel):
    query: str
    org_id: str
    chat_history: List[Dict[str, str]]

class EnterpriseRAGService:
    def __init__(self):
        # In a real scenario, initialize Pinecone client, LLM gateways, and Cross-Encoders here.
        self.vector_db = "Pinecone"
        self.llm = "GPT-4o / Claude 3 Opus"
        self.reranker = "Cohere / BGE-Reranker-Large"

    async def rewrite_query(self, query: str) -> str:
        """
        Translates a conversational query ("How do I do this?") 
        into a dense semantic search query using chat history.
        """
        return f"[Rewritten for Semantics] {query}"

    async def hybrid_search(self, query: str, org_id: str) -> List[dict]:
        """
        Executes Dense (Vector) + Sparse (BM25) search on Pinecone.
        Crucially applies the metadata filter: {"org_id": {"$eq": org_id}} for absolute data isolation.
        """
        # Mock retrieval
        return [
            {"id": "doc_1", "text": "OAuth2 authentication requires a Bearer token.", "metadata": {"source": "auth.md"}},
            {"id": "doc_2", "text": "Rate limits are 100 req/sec per tenant.", "metadata": {"source": "limits.md"}}
        ]

    async def rerank_results(self, query: str, documents: List[dict]) -> List[dict]:
        """
        Passes the top 50 hybrid search results through a Cross-Encoder to extract the true Top 5.
        """
        # Mock reranking
        return documents[:3]

    async def generate_streaming_answer(self, query: RAGQuery) -> AsyncGenerator[str, None]:
        """
        The core engine. Performs RAG and yields Server-Sent Events (SSE) chunks.
        """
        try:
            # 1. Rewrite Query
            optimized_query = await self.rewrite_query(query.query)
            
            # 2. Retrieve & Rerank (Strictly isolated to org_id)
            raw_docs = await self.hybrid_search(optimized_query, query.org_id)
            top_docs = await self.rerank_results(optimized_query, raw_docs)
            
            # 3. Context Construction
            context = "\n\n".join([d["text"] for d in top_docs])
            system_prompt = (
                "You are an Enterprise Support Engineer. "
                "Use the following context strictly. Output exactly in the requested Markdown hierarchy."
                f"\n\nContext:\n{context}"
            )
            
            # 4. Stream LLM Response (Mocked generation loop for demonstration)
            # In production, this uses `async for chunk in llm.astream(...)`
            yield "data: " + json.dumps({"type": "status", "content": "Retrieving context..."}) + "\n\n"
            await asyncio.sleep(0.5)
            
            mock_answer = "### QUICK_ANSWER\nTo authenticate, use a Bearer token.\n\n### CODE\n```bash\ncurl -H 'Authorization: Bearer <TOKEN>'\n```"
            
            for word in mock_answer.split(" "):
                chunk = json.dumps({"type": "content", "content": word + " "})
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.05)
                
            # 5. Send Source Attributions
            sources_payload = json.dumps({"type": "sources", "content": [d["metadata"] for d in top_docs]})
            yield f"data: {sources_payload}\n\n"
            
            # 6. End Stream
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_payload = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_payload}\n\n"

rag_service = EnterpriseRAGService()
