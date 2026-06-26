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

def check_guardrails(question: str) -> bool:
    """
    Checks if a query is safe and relevant.
    Returns True if ALLOWED, False if BLOCKED.
    """
    try:
        llm = initialize_llm()
        prompt = PromptTemplate(template=GUARDRAILS_PROMPT, input_variables=["question"])
        chain = prompt | llm
        
        response = chain.invoke({"question": question})
        result = response.content.strip().upper()
        return "ALLOWED" in result
    except (ChatGoogleGenerativeAIError, GoogleGenerativeAIError, Exception) as e:
        err_str = str(e)
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "NOT_FOUND" in err_str or "PERMISSION_DENIED" in err_str:
            logger.warning("Gemini quota exceeded or access denied. Skipping guardrails.")
            return True # Allow the query if guardrails fail due to quota
        logger.error(f"Unexpected error in guardrails: {e}")
        return True

def rewrite_query(question: str) -> str:
    """
    Rewrites a vague query into a specific one.
    """
    try:
        llm = initialize_llm()
        prompt = PromptTemplate(template=REWRITE_PROMPT, input_variables=["question"])
        chain = prompt | llm
        
        response = chain.invoke({"question": question})
        return response.content.strip()
    except (ChatGoogleGenerativeAIError, GoogleGenerativeAIError, Exception) as e:
        err_str = str(e)
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "NOT_FOUND" in err_str or "PERMISSION_DENIED" in err_str:
            logger.warning("Gemini quota exceeded or access denied. Skipping query optimization.")
            return question # Return original query
        logger.error(f"Unexpected error in query rewriting: {e}")
        return question

def generate_answer(question: str, context: str, memory=None, retriever=None) -> str:
    """
    Generates an answer using a direct, robust RAG pipeline.
    Implements empty context protection, validation, and failover retries.
    """
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
            llm = initialize_llm()
            chain = prompt | llm | StrOutputParser()
            
            full_response = ""
            for chunk in chain.stream(chain_input):
                full_response += chunk
                yield chunk
                
            # 4. Empty Response Protection (Answer Validation)
            if not full_response.strip():
                logger.warning(f"Empty response received on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue # Retry
                else:
                    yield "I found related documentation but couldn't generate a reliable answer. Please try rephrasing your question."
            
            # Successfully generated answer
            return
            
        except Exception as e:
            logger.error(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                yield "An unexpected error occurred while generating the answer. Please ensure your API keys and quotas are valid, and try again."
