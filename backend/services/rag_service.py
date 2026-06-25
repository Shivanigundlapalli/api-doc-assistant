import json
import asyncio
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
        # We will use Gemini Pro as the default for the API
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=settings.OPENAI_API_KEY, # Using the setting field temporarily
            temperature=0
        )
        
        self.system_prompt = """You are an Enterprise Documentation AI Agent used in production by millions of users.

Your job is to answer questions exactly like a world-class documentation assistant built by companies such as OpenAI, Stripe, GitHub, Notion, and Intercom.

# PRIMARY OBJECTIVE
Provide: Correct answers, Grounded answers, Fast answers, No hallucinations, High trust and reliability.
Never optimize for sounding smart. Always optimize for correctness.

# GOLDEN RULE
Only answer from the retrieved documentation context.
Never invent APIs, endpoints, limits, features, SDKs, examples, or configuration values.
If information is unavailable, say: "I could not find this information in the available documentation."

# HALLUCINATION GUARDRAILS
If confidence < 0.70, retrieved context is insufficient, or sources disagree:
Do NOT answer speculatively. Respond: "I could not find a definitive answer in the available documentation."

# CONFIDENCE LEVELS
Verified: Answer directly supported by documentation.
Partial: Requires combining multiple documents.
Low: Documentation is insufficient.

# RESPONSE FORMAT
You MUST output your response exactly using these Markdown headers so the UI can parse it.
### CONFIDENCE
### QUICK_ANSWER
### KEY_DETAILS
### CODE_EXAMPLE
### DEVELOPER_ACTIONS
### EDGE_CASES_AND_WARNINGS
### SOURCE_SNIPPETS
### SOURCES
### RELATED_DOCUMENTATION
### RELATED_QUESTIONS

# CITATION RULES
Every factual statement must be traceable to at least one source. Do not cite unused documents.
"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Context: {context}\n\nQuestion: {question}")
        ])

    async def rewrite_query(self, query: str) -> str:
        # Placeholder for query rewriting agent
        return query

    async def hybrid_search(self, query: str, org_id: str) -> List[dict]:
        # Placeholder for Pinecone Hybrid Search
        return [
            {"id": "doc_1", "text": "OAuth2 requires a Bearer token.", "metadata": {"source": "auth.md"}},
        ]

    async def generate_streaming_answer(self, query: RAGQuery) -> AsyncGenerator[str, None]:
        try:
            # 1. Rewrite & Retrieve
            optimized_query = await self.rewrite_query(query.query)
            top_docs = await self.hybrid_search(optimized_query, query.org_id)
            context = "\n\n".join([d["text"] for d in top_docs])
            
            # 2. Setup streaming chain
            chain = self.prompt | self.llm | StrOutputParser()
            
            yield "data: " + json.dumps({"type": "status", "content": "Retrieving context..."}) + "\n\n"
            
            # 3. Stream from LangChain asynchronously
            async for chunk_text in chain.astream({"context": context, "question": optimized_query}):
                payload = json.dumps({"type": "content", "content": chunk_text})
                yield f"data: {payload}\n\n"
                
            # 4. Sources
            sources_payload = json.dumps({"type": "sources", "content": [d["metadata"] for d in top_docs]})
            yield f"data: {sources_payload}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_payload = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_payload}\n\n"

rag_service = EnterpriseRAGService()
