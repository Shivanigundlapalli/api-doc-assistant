import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError, GoogleGenerativeAIError
from langchain.prompts import PromptTemplate, ChatPromptTemplate
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

def generate_answer(question: str, context: str, memory=None) -> str:
    """
    Generates an answer based on the context and conversation history,
    with dynamic retries and fallback across available models during inference.
    """
    api_key = get_google_api_key()
    
    MODELS = [
        get_primary_model(),
        get_fallback_model()
    ]
    
    MAX_RETRIES = 1
    RETRY_DELAY = 2
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", QA_SYSTEM_PROMPT),
        ("human", RETRIEVAL_PROMPT)
    ])
    
    # Format memory string
    memory_str = ""
    if memory:
        # Include up to the last 4 exchanges to keep context window reasonable
        for m in memory[-4:]:
            memory_str += f"User: {m['question']}\nAssistant: {m['answer']}\n\n"
    if not memory_str:
        memory_str = "No previous conversation."
    
    for attempt in range(MAX_RETRIES):
        for model_name in MODELS:
            logger.info(f"Using Gemini model: {model_name}")
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0,
                    timeout=15
                )
                chain = prompt | llm | StrOutputParser()
                yield from chain.stream({"context": context, "memory": memory_str, "question": question})
                return
            except (ChatGoogleGenerativeAIError, GoogleGenerativeAIError, Exception) as e:
                err_str = str(e)
                logger.warning(f"Generation failed with model {model_name} (Attempt {attempt+1}/{MAX_RETRIES}): {err_str}")
                
        # If all Gemini models fail, try Ollama
        if use_ollama_fallback():
            logger.info("Falling back to Ollama")
            from langchain_ollama import ChatOllama
            ollama_model = get_ollama_model()
            try:
                llm = ChatOllama(model=ollama_model, temperature=0)
                chain = prompt | llm | StrOutputParser()
                yield from chain.stream({"context": context, "memory": memory_str, "question": question})
                return
            except Exception as e:
                logger.warning(f"Ollama unavailable. Fallback {ollama_model} also failed: {e}")
                
        if attempt < MAX_RETRIES - 1:
            st.warning(f"APIs temporarily unavailable. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            
    logger.error("All fallback chains exhausted for generation.")
    yield "Gemini API quota exceeded.\nPlease try again later or use another API key."
