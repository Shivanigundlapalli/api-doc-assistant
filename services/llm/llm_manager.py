import time
import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from config import get_google_api_key, get_openai_api_key, get_primary_model, get_fallback_model, get_ollama_model
from services.logging.logger import get_logger
from services.error_handler.handler import handle_exception, PipelineError

logger = get_logger("LLMManager")

def get_llm_chain_with_failover(prompt_template, output_parser):
    """
    Returns a function that executes the chain with backoff and failover.
    """
    google_key = get_google_api_key()
    openai_key = get_openai_api_key()
    
    models_to_try = [
        ("Gemini 2.5 Flash", lambda: ChatGoogleGenerativeAI(model=get_primary_model(), google_api_key=google_key, temperature=0)),
        ("Gemini 2.0 Flash", lambda: ChatGoogleGenerativeAI(model=get_fallback_model(), google_api_key=google_key, temperature=0))
    ]
    
    if openai_key:
        models_to_try.append(("GPT-4o Mini", lambda: ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0)))
        
    models_to_try.append(("Local Ollama", lambda: ChatOllama(model=get_ollama_model(), temperature=0)))

    def execute_chain(inputs: dict):
        backoff_delays = [1, 2, 4, 8]
        
        for model_name, model_init_fn in models_to_try:
            logger.info(f"Attempting to use model: {model_name}")
            
            for attempt, delay in enumerate(backoff_delays + [0]):
                try:
                    llm = model_init_fn()
                    chain = prompt_template | llm | output_parser
                    
                    start_time = time.time()
                    # We will collect chunks instead of yielding here, because LangGraph nodes return state
                    # Wait, if we want streaming, we should return a generator.
                    # But the prompt asks to return the generator from the node.
                    def stream_generator():
                        full_res = ""
                        for chunk in chain.stream(inputs):
                            full_res += chunk
                            yield chunk
                        logger.info(f"[{model_name}] Generation complete. Length: {len(full_res)}. Latency: {time.time()-start_time:.2f}s")
                    
                    # We need to test if it fails immediately (e.g. 429). We can't catch 429 if we return the generator immediately.
                    # To truly catch 429 on stream start, we could buffer the first chunk.
                    iterator = chain.stream(inputs)
                    first_chunk = next(iterator, None)
                    
                    def safe_stream_generator():
                        if first_chunk:
                            yield first_chunk
                        for chunk in iterator:
                            yield chunk
                            
                    return safe_stream_generator(), model_name
                    
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "exhausted" in err_str or "503" in err_str or "timeout" in err_str:
                        if delay > 0:
                            logger.warning(f"[{model_name}] Transient error (e.g. 429). Retrying in {delay}s... ({e})")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"[{model_name}] Exhausted retries.")
                            break # Move to next model
                    elif "403" in err_str or "not found" in err_str or "api key" in err_str:
                        logger.error(f"[{model_name}] Fatal auth/config error. Skipping to next model. ({e})")
                        break # Move to next model
                    else:
                        logger.error(f"[{model_name}] Unexpected error: {e}. Skipping to next model.")
                        break # Move to next model

        raise PipelineError("LLM", "We couldn't generate an answer because the language model is temporarily unavailable.")
        
    return execute_chain
