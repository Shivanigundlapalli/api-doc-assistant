import asyncio
import json
from services.rag_service import rag_service, RAGQuery

test_questions = [
    "How do authentication and rate limits work together?",
    "Summarize all response headers for a new developer.",
    "What happens if the X-RateLimit-Remaining header reaches zero?",
    "Does the API return Retry-After headers?",
    "Which document defines the X-RateLimit-Reset header?",
    "Explain how authentication, rate limits, and response headers work together."
]

async def run_tests():
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {question}")
        print(f"{'='*80}\n")
        
        query = RAGQuery(query=question, org_id="test_org", chat_history=[])
        
        full_response = ""
        metadata = None
        sources = []
        
        async for chunk in rag_service.generate_streaming_answer(query):
            if chunk.startswith("data: "):
                data_str = chunk.replace("data: ", "").strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if data["type"] == "metadata":
                        metadata = data["content"]
                        print(f"📊 METADATA: Confidence: {metadata['confidence']}% | Sources: {metadata['sources']} | Chunks: {metadata['chunks']} | Latency: {metadata['latency']}\n")
                    elif data["type"] == "content":
                        full_response += data["content"]
                        print(data["content"], end="", flush=True)
                    elif data["type"] == "sources":
                        sources = data["content"]
                except Exception as e:
                    pass
        
        print("\n\n🔍 SOURCES USED:")
        for s in sources:
            print(f"- {s['source']} (Section: {s.get('section', 'N/A')})")
            print(f"  Snippet: \"{s['text'][:100]}...\"")
        print("\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
