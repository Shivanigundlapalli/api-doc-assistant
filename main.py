import os
from dotenv import load_dotenv

def run_evaluation():
    """
    Runs an evaluation pipeline over test_questions.txt
    Requires LangSmith configuration.
    """
    load_dotenv()
    
    if not os.path.exists("test_questions.txt"):
        print("test_questions.txt not found. Creating a sample file.")
        with open("test_questions.txt", "w") as f:
            f.write("How do I authenticate?\n")
            f.write("What is the rate limit?\n")
            f.write("login issue\n")
            
    print("Starting Evaluation Pipeline...")
    print("Reading questions from test_questions.txt...")
    
    # Import services
    from services.evaluation_service import initialize_langsmith
    from services.vector_store_service import initialize_vector_store, get_retriever
    from services.llm_service import generate_answer, check_guardrails, rewrite_query
    from utils.text_processing import deduplicate_docs
    
    initialize_langsmith()
    
    vector_store = initialize_vector_store()
    retriever = get_retriever(vector_store) if vector_store else None
    
    if not retriever:
        print("Error: Vector store is not initialized. Run app first to build the DB.")
        return
        
    with open("test_questions.txt", "r") as f:
        questions = [q.strip() for q in f.readlines() if q.strip()]
        
    for q in questions:
        print(f"\nEvaluating Query: '{q}'")
        
        is_allowed = check_guardrails(q)
        if not is_allowed:
            print("  Result: BLOCKED by Guardrails")
            continue
            
        optimized_q = rewrite_query(q)
        print(f"  Optimized Query: '{optimized_q}'")
        
        raw_docs = retriever.invoke(optimized_q)
        docs = deduplicate_docs(raw_docs)
        print(f"  Retrieved {len(docs)} chunks.")
        
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = generate_answer(optimized_q, context)
        
        print(f"  Answer Preview: {answer[:100]}...")
        
    print("\nEvaluation Complete! Check LangSmith dashboard for traces.")

if __name__ == "__main__":
    run_evaluation()
