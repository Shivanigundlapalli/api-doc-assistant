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
        
        self.system_prompt = """You are an Enterprise Documentation AI Agent.

Your goal is to answer questions exactly like a production SaaS documentation assistant used by companies such as Stripe, OpenAI, GitHub, and Intercom.

# Core Rules
NEVER hallucinate.
NEVER invent APIs, limits, endpoints, features, or documentation.
Answer ONLY from the retrieved documentation context.
If the answer is not present in the documentation, respond:
"I could not find this information in the available documentation."

# Confidence Rules
Confidence = Verified by Documentation: Answer is directly supported by documentation.
Confidence = Partial: Answer requires combining multiple documents.
Confidence = Low: Documentation does not contain enough information.

# Response Format
You MUST output your response exactly using these Markdown headers so the UI can parse it.
### CONFIDENCE
### QUICK_ANSWER
### KEY_DETAILS
### CODE_EXAMPLE
### DEVELOPER_ACTIONS
### EDGE_CASES_AND_WARNINGS
### SOURCES
### RELATED_DOCUMENTATION

# Answering Principle
Correct answer with insufficient information is better than an incorrect answer with high confidence.
Always prefer: Grounded Answer > Incomplete Answer > Speculative Answer.
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
