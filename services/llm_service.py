import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError, GoogleGenerativeAIError
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from google.generativeai.types import generation_types
from google.api_core.exceptions import GoogleAPIError

from prompts.system_prompts import QA_SYSTEM_PROMPT, GUARDRAILS_PROMPT, RETRIEVAL_PROMPT
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

from langchain_core.prompts import PromptTemplate
from prompts.system_prompts import ANALYZER_PROMPT, COMPRESSOR_PROMPT
import json

def analyze_query(question: str, memory: list = None) -> dict:
    """
    Fast heuristics-based Query Understanding.
    Rewrites the query using conversation memory without a slow LLM call.
    """
    category = "General"
    question_lower = question.lower()
    
    # Intent Detection Heuristics
    if any(k in question_lower for k in ["auth", "token", "key", "secret", "oauth"]):
        category = "Authentication"
    elif any(k in question_lower for k in ["error", "400", "401", "404", "500", "fail", "bug"]):
        category = "Errors"
    elif any(k in question_lower for k in ["rate", "limit", "quota", "maximum", "exceed"]):
        category = "Rate Limits"
    elif any(k in question_lower for k in ["sdk", "python", "javascript", "curl"]):
        category = "SDK & Examples"
        
    # Simple Contextual Rewrite based on memory
    rewritten_query = question
    if memory and len(question.split()) <= 3:
        last_q = memory[-1].get("question", "")
        if "key" in question_lower or "it" in question_lower:
            rewritten_query = f"{last_q} {question}"
            
    return {"rewritten_query": rewritten_query, "category": category}

def compress_context(question: str, chunks: list) -> str:
    """
    Fast string-based context compressor.
    Removes exact duplicates and limits total characters to avoid context bloat.
    """
    seen = set()
    compressed = []
    
    for c in chunks:
        # Simple deduplication by first 100 characters
        sig = c.page_content[:100]
        if sig not in seen:
            seen.add(sig)
            compressed.append(c.page_content)
            
    # Join and limit to ~15,000 characters
    return "\n\n---\n\n".join(compressed)[:15000]

def rerank_and_score_confidence(question: str, chunks: list, top_k: int = 3) -> dict:
    """
    Fast Lexical & Semantic Reranker.
    Uses keyword overlap to score and rank chunks instantly.
    """
    if not chunks:
        return {"top_chunks": [], "confidence": 0}
        
    question_terms = set(re.findall(r'\w+', question.lower()))
    
    scored_chunks = []
    for chunk in chunks:
        content_lower = chunk.page_content.lower()
        chunk_terms = set(re.findall(r'\w+', content_lower))
        
        # Calculate Jaccard-like overlap score
        overlap = len(question_terms.intersection(chunk_terms))
        score = (overlap / max(len(question_terms), 1)) * 100
        
        # Boost score if exact phrase matches
        if question.lower() in content_lower:
            score += 30
            
        # Boost for API specifics
        if "api" in question_lower and "endpoint" in content_lower:
            score += 10
            
        scored_chunks.append((score, chunk))
        
    # Sort by score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_chunks = [c for score, c in scored_chunks[:top_k]]
    
    # Calculate confidence based on the top score
    best_score = scored_chunks[0][0]
    
    if best_score > 60:
        confidence = 95
    elif best_score > 30:
        confidence = 75
    else:
        confidence = 45 # Low confidence
        
    return {"top_chunks": top_chunks, "confidence": confidence}

def generate_answer(question: str, context: str, memory=None, retriever=None) -> str:
    """
    Generates an answer using a fast, single-pass LCEL Chain.
    Replaces the slow ReAct agent to prevent duplicated retrieval.
    """
    start_time = time.time()
    
    # Format Memory
    chat_history = ""
    if memory:
        chat_history = "\n".join([f"User: {m.get('question', '')}\nAssistant: {m.get('answer', '')}" for m in memory[-3:]])
            
    prompt = PromptTemplate.from_template(
        QA_SYSTEM_PROMPT + "\n\n"
        "--- CONVERSATION HISTORY ---\n{chat_history}\n\n"
        "--- RETRIEVED DOCUMENTATION ---\n{context}\n\n"
        "User Question: {question}"
    )

    # Failover & Retry Execution
    max_retries = 2
    for attempt in range(max_retries):
        try:
            llm_start_time = time.time()
            llm = initialize_llm()
            chain = prompt | llm | StrOutputParser()
            
            full_response = ""
            for chunk in chain.stream({
                "chat_history": chat_history,
                "context": context,
                "question": question
            }):
                full_response += chunk
                yield chunk
                
            llm_end_time = time.time()
            llm_time = llm_end_time - llm_start_time
            total_time = llm_end_time - start_time
            
            # Answer Validation (Length > 20)
            if not full_response or len(full_response.strip()) <= 20:
                logger.warning(f"Answer validation failed on attempt {attempt + 1}: length {len(full_response)} <= 20")
                if attempt < max_retries - 1:
                    continue # Retry
                else:
                    yield "I found related documentation but couldn't generate a reliable answer. Please try rephrasing your question."
                    return
            
            # Pipeline Report
            print("\n" + "="*50)
            print("PIPELINE REPORT")
            print("="*50)
            print(f"LLM Time: {llm_time:.3f}s")
            print(f"Total Generation Time: {total_time:.3f}s")
            print(f"Answer Length: {len(full_response)} chars")
            print("="*50 + "\n")
            
            return
            
        except Exception as e:
            logger.error(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                yield "The AI service is temporarily unavailable. Please try again."
