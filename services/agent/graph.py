import logging
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from services.agent.tools import check_guardrails, analyze_query
from services.retriever.retriever_manager import retrieve_chunks
from services.reranker_service import deduplicate_docs, rerank_and_score_confidence, compress_context
from services.prompt_service import build_qa_prompt
from services.error_handler.handler import PipelineError, handle_exception
from services.logging.logger import log_stage, get_logger
from langchain_core.output_parsers import StrOutputParser
import time

logger = get_logger("AgentGraph")

class AgentState(TypedDict):
    question: str
    memory: List[Dict[str, Any]]
    retriever: Any
    is_allowed: bool
    optimized_query: str
    category: str
    raw_docs: List[Any]
    deduped_docs: List[Any]
    top_docs: List[Any]
    confidence: int
    compressed_context: str
    error_message: str
    answer_stream: Any
    final_model: str

def safe_node(stage_name: str):
    def decorator(func):
        def wrapper(state: AgentState):
            try:
                logger.info(f"[{stage_name}] Node entered.")
                logger.debug(f"[{stage_name}] Input State: {list(state.keys())}")
                
                start_time = time.time()
                result = func(state)
                elapsed = time.time() - start_time
                
                logger.info(f"[{stage_name}] Node exited in {elapsed:.2f}s.")
                logger.debug(f"[{stage_name}] Output: {list(result.keys()) if result else None}")
                
                if "error_message" not in result:
                    log_stage(stage_name, "Success", {"latency": f"{elapsed:.2f}s"})
                return result
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                logger.error(f"[{stage_name}] EXCEPTION OCCURRED:\n{tb}")
                
                err_json = handle_exception(stage_name, e)
                return {"error_message": err_json}
        return wrapper
    return decorator

@safe_node("Guardrails")
def node_guardrails(state: AgentState):
    is_allowed = check_guardrails(state["question"])
    if not is_allowed:
        raise PipelineError("Guardrails", "I can answer only questions related to the uploaded documentation.")
    return {"is_allowed": True}

@safe_node("Query Rewrite")
def node_analyze_query(state: AgentState):
    analysis = analyze_query(state["question"], state["memory"])
    return {
        "optimized_query": analysis["rewritten_query"],
        "category": analysis["category"]
    }

@safe_node("Retriever")
def node_retrieve(state: AgentState):
    docs = retrieve_chunks(state.get("retriever"), state["optimized_query"], top_k=8)
    log_stage("Retriever", "Documents retrieved", {"count": len(docs)})
    return {"raw_docs": docs}

@safe_node("Re-ranker")
def node_rerank(state: AgentState):
    deduped = deduplicate_docs(state.get("raw_docs", []))
    rerank_result = rerank_and_score_confidence(state["optimized_query"], deduped, top_k=4)
    log_stage("Re-ranker", "Top chunks selected", {"count": len(rerank_result["top_chunks"]), "confidence": rerank_result["confidence"]})
    return {
        "deduped_docs": deduped,
        "top_docs": rerank_result["top_chunks"],
        "confidence": rerank_result["confidence"]
    }

@safe_node("Context Validation")
def node_context_validation(state: AgentState):
    top_docs = state.get("top_docs", [])
    confidence = state.get("confidence", 0)
    raw_docs = state.get("raw_docs", [])
    
    if len(top_docs) == 0 or confidence < 10:
        # Extract unique source names
        unique_names = set()
        for doc in raw_docs:
            metadata = getattr(doc, "metadata", {})
            raw_name = metadata.get("source", metadata.get("name", "Unknown Source"))
            name = str(raw_name).split('/')[-1].split('\\')[-1]
            unique_names.add(name)
            
        searched_list = "\n".join([f"• {name}" for name in unique_names]) if unique_names else "• No documents indexed"
        
        err_msg = (
            f"I couldn't find information about \"{state['question']}\" in the uploaded documentation.\n\n"
            f"I searched:\n{searched_list}\n\n"
            "If you upload documentation containing this topic, I'll answer based on those documents."
        )
        raise PipelineError("Context Validation", err_msg)
        
    context = compress_context(top_docs)
    if len(context) < 50:
        err_msg = (
            f"I couldn't find information about \"{state['question']}\" in the uploaded documentation.\n\n"
            "If you upload documentation containing this topic, I'll answer based on those documents."
        )
        raise PipelineError("Context Validation", err_msg)
        
    return {"compressed_context": context}

@safe_node("LLM")
def node_llm(state: AgentState):
    from services.llm.provider_manager import ProviderManager
    
    prompt = build_qa_prompt(state["optimized_query"], state["compressed_context"], state["memory"])
    pm = ProviderManager()
    
    inputs = {
        "chat_history": "", 
        "context": state["compressed_context"],
        "question": state["optimized_query"]
    }
    
    # Debug logging
    formatted_prompt = prompt.format(**inputs)
    logger.debug(f"[LLM Debug] Formatted prompt length: {len(formatted_prompt)} chars")
    logger.debug(f"[LLM Debug] Context length: {len(state['compressed_context'])} chars")
    
    answer_stream, final_model = pm.execute_with_failover(prompt, StrOutputParser(), inputs)
    return {"answer_stream": answer_stream, "final_model": final_model}

@safe_node("Response Validator")
def node_response_validator(state: AgentState):
    if not state.get("answer_stream"):
        raise PipelineError("Response Validator", "We couldn't generate a valid answer because the language model response was empty.")
    return {}

def create_production_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("guardrails", node_guardrails)
    workflow.add_node("analyze_query", node_analyze_query)
    workflow.add_node("retrieve", node_retrieve)
    workflow.add_node("rerank", node_rerank)
    workflow.add_node("context_validation", node_context_validation)
    workflow.add_node("llm", node_llm)
    workflow.add_node("response_validator", node_response_validator)

    workflow.set_entry_point("guardrails")

    def check_error_edge(state: AgentState):
        if state.get("error_message"):
            return "end"
        return "continue"

    workflow.add_conditional_edges("guardrails", check_error_edge, {"continue": "analyze_query", "end": END})
    workflow.add_conditional_edges("analyze_query", check_error_edge, {"continue": "retrieve", "end": END})
    workflow.add_conditional_edges("retrieve", check_error_edge, {"continue": "rerank", "end": END})
    workflow.add_conditional_edges("rerank", check_error_edge, {"continue": "context_validation", "end": END})
    workflow.add_conditional_edges("context_validation", check_error_edge, {"continue": "llm", "end": END})
    workflow.add_conditional_edges("llm", check_error_edge, {"continue": "response_validator", "end": END})
    workflow.add_conditional_edges("response_validator", check_error_edge, {"continue": END, "end": END})

    return workflow.compile()
