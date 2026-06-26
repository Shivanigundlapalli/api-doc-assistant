import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError, GoogleGenerativeAIError
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from google.generativeai.types import generation_types
from google.api_core.exceptions import GoogleAPIError

from prompts.system_prompts import QA_SYSTEM_PROMPT, REWRITE_PROMPT, GUARDRAILS_PROMPT, RETRIEVAL_PROMPT
from config import (
    get_google_api_key,
    get_primary_model,
    get_fallback_model,
    get_ollama_model,
    use_ollama_fallback
)

import time
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def initialize_llm():
    try:
        api_key = get_google_api_key()
    except ValueError as e:
        st.error(str(e))
        # Wait until the user configures the API key
        st.stop()
        
    last_error = None
    
    # 1. Try Primary Gemini Model
    primary_model = get_primary_model()
    try:
        llm = ChatGoogleGenerativeAI(
            model=primary_model, 
            google_api_key=api_key, 
            temperature=0
        )
        llm.invoke("test")
        logger.info(f"Successfully connected to Primary Gemini model: {primary_model}")
        return llm
    except Exception as e:
        logger.warning(f"Primary model {primary_model} failed: {e}")
        last_error = e

    # 2. Try Fallback Gemini Model
    fallback_model = get_fallback_model()
    try:
        llm = ChatGoogleGenerativeAI(
            model=fallback_model, 
            google_api_key=api_key, 
            temperature=0
        )
        llm.invoke("test")
        logger.info(f"Successfully connected to Fallback Gemini model: {fallback_model}")
        return llm
    except Exception as e:
        logger.warning(f"Fallback model {fallback_model} failed: {e}")
        last_error = e

    # 3. Try Ollama if enabled
    if use_ollama_fallback():
        logger.info("Falling back to Ollama")
        from langchain_ollama import ChatOllama
        ollama_model = get_ollama_model()
        try:
            llm = ChatOllama(model=ollama_model, temperature=0)
            llm.invoke("test")
            logger.info(f"Successfully connected to Ollama fallback model: {ollama_model}")
            return llm
        except Exception as e:
            logger.warning(f"Ollama unavailable. Model {ollama_model} failed: {e}")
            last_error = e

    st.error("All AI models failed to initialize. Please check your API keys or local Ollama setup.")
    st.info(f"Last error encountered: {last_error}")
    st.stop()

import re

def check_guardrails(question: str) -> bool:
    """
    Checks if a query is safe and relevant using high-speed Python heuristics instead of an LLM.
    Returns True if ALLOWED, False if BLOCKED.
    """
    blocked_keywords = [
        "ignore previous instructions", "you are now a", "system prompt",
        "medical advice", "legal advice", "hack", "bypass", "exploit"
    ]
    question_lower = question.lower()
    for keyword in blocked_keywords:
        if keyword in question_lower:
            logger.warning(f"Guardrails blocked query for keyword: {keyword}")
            return False
            
    return True

def rewrite_query(question: str) -> str:
    """
    Bypasses LLM rewriting for speed optimization. Returns original query.
    """
    return question.strip()

def generate_answer(question: str, context: str, memory=None, retriever=None) -> str:
    """
    Generates an answer using a direct, robust RAG pipeline.
    Implements empty context protection, validation (len > 20), failover retries, and detailed telemetry.
    """
    start_time = time.time()
    
    # 1. Source Validation
    if not context or not context.strip():
        yield "I searched the uploaded documentation but couldn't find information about this topic.\n\n**Related topics you might explore:**\n- Authentication\n- Rate Limits\n- API Keys"
        return

    # 2. Format Prompt and Memory
    prompt = ChatPromptTemplate.from_messages([
        ("system", QA_SYSTEM_PROMPT),
        ("user", RETRIEVAL_PROMPT)
    ])
    
    memory_str = ""
    if memory:
        for m in memory[-3:]: # Include last 3 interactions
            memory_str += f"User: {m.get('question', '')}\nAssistant: {m.get('answer', '')}\n\n"
            
    chain_input = {
        "context": context,
        "memory": memory_str if memory_str else "No prior conversation.",
        "question": question
    }

    # 3. Failover & Retry Execution
    max_retries = 2
    for attempt in range(max_retries):
        try:
            llm_start_time = time.time()
            llm = initialize_llm()
            chain = prompt | llm | StrOutputParser()
            
            full_response = ""
            for chunk in chain.stream(chain_input):
                full_response += chunk
                yield chunk
                
            llm_end_time = time.time()
            llm_time = llm_end_time - llm_start_time
            total_time = llm_end_time - start_time
            
            # 4. Answer Validation (Length > 20)
            if not full_response or len(full_response.strip()) <= 20:
                logger.warning(f"Answer validation failed on attempt {attempt + 1}: length {len(full_response)} <= 20")
                if attempt < max_retries - 1:
                    continue # Retry
                else:
                    yield "I found related documentation but couldn't generate a reliable answer. Please try rephrasing your question."
                    return
            
            # 5. Pipeline Report
            print("\n" + "="*50)
            print("PIPELINE REPORT")
            print("="*50)
            print(f"LLM Time: {llm_time:.3f}s")
            print(f"Total Generation Time: {total_time:.3f}s")
            print(f"Answer Length: {len(full_response)} chars")
            print(f"Model Used: {get_primary_model() if attempt == 0 else get_fallback_model()}")
            print("="*50 + "\n")
            
            # Successfully generated answer
            return
            
        except Exception as e:
            logger.error(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                yield "An unexpected error occurred while generating the answer. Please ensure your API keys and quotas are valid, and try again."
