import json
import asyncio
import time
from typing import AsyncGenerator, List, Dict
from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from core.config import settings

class RAGQuery(BaseModel):
    query: str
    org_id: str
    chat_history: List[Dict[str, str]]

class EnterpriseRAGService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=settings.OPENAI_API_KEY, 
            temperature=0
        )
        
        self.system_prompt = """You are an Enterprise Documentation AI Agent used in production by millions of users.

# GOLDEN RULE
Only answer from the retrieved documentation context.
Never invent APIs, endpoints, limits, features, SDKs, examples, or configuration values.
If information is unavailable, say: "I could not find this information in the available documentation."

# HALLUCINATION GUARDRAILS
If retrieved context is insufficient or sources disagree:
Do NOT answer speculatively. Respond exactly with: "I could not find a definitive answer in the available documentation."

# RESPONSE FORMAT
You MUST output your response exactly using these Markdown headers so the UI can parse it.
### QUICK_ANSWER
### KEY_DETAILS
### CODE_EXAMPLE
### DEVELOPER_ACTIONS
### EDGE_CASES_AND_WARNINGS
### SOURCE_SNIPPETS
### RELATED_DOCUMENTATION
### RELATED_QUESTIONS

# CITATION RULES
Every factual statement must be traceable to at least one source. Do not cite unused documents.
You MUST append an inline citation immediately after every factual claim in this format: [filename.md]
"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])

    async def rewrite_query(self, query: str) -> str:
        return query

    async def hybrid_search(self, query: str, org_id: str) -> List[dict]:
        # Mocking retrieval metadata for the 10/10 UX
        return [
            {"id": "doc_1", "text": "The Free plan allows 100 requests/minute. Exceeding this returns a 429 error.", "metadata": {"source": "rate_limits.md"}},
            {"id": "doc_2", "text": "OAuth2 requires a Bearer token in the Authorization header.", "metadata": {"source": "auth.md"}},
            {"id": "doc_3", "text": "API Keys must be prefixed with 'sk_live_'.", "metadata": {"source": "api_keys.md"}},
        ]

    async def generate_streaming_answer(self, query: RAGQuery) -> AsyncGenerator[str, None]:
        start_time = time.time()
        try:
            # 1. Rewrite & Retrieve
            optimized_query = await self.rewrite_query(query.query)
            top_docs = await self.hybrid_search(optimized_query, query.org_id)
            context = "\n\n".join([d["text"] for d in top_docs])
            
            # Simulated Reranking Confidence Logic
            chunks_retrieved = len(top_docs)
            sources_used = len(set(d["metadata"]["source"] for d in top_docs))
            simulated_confidence = 96 if chunks_retrieved > 0 else 0
            
            latency = f"{(time.time() - start_time):.1f}s"
            
            # Emit Metadata payload for UI
            metadata_payload = {
                "confidence": simulated_confidence,
                "sources": sources_used,
                "chunks": chunks_retrieved,
                "latency": latency
            }
            yield f"data: {json.dumps({'type': 'metadata', 'content': metadata_payload})}\n\n"
            
            # 2. Setup streaming chain
            chain = self.prompt | self.llm | StrOutputParser()
            
            # 3. Stream from LangChain asynchronously
            async for chunk_text in chain.astream({"context": context, "question": optimized_query}):
                payload = json.dumps({"type": "content", "content": chunk_text})
                yield f"data: {payload}\n\n"
                
            # 4. Sources with full text for Snippets
            sources_payload = json.dumps({"type": "sources", "content": [
                {"source": d["metadata"]["source"], "text": d["text"]} for d in top_docs
            ]})
            yield f"data: {sources_payload}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_payload = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_payload}\n\n"

rag_service = EnterpriseRAGService()
