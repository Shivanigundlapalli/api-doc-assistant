import asyncio
import json
from services.rag_service import rag_service, RAGQuery

test_questions = [
    "Does the API support GraphQL?",
    "Invent a new API endpoint.",
    "Tell me something about the API that is not in the documentation."
]

async def run_tests():
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {question}")
        print(f"{'='*80}\n")
        
        query = RAGQuery(query=question, org_id="test_org", chat_history=[])
        
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
                        print(data["content"], end="", flush=True)
                except Exception as e:
                    pass
        print("\n")

if __name__ == "__main__":
    asyncio.run(run_tests())
