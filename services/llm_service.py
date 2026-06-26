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
    LLM-powered Query Understanding.
    Rewrites the query and categorizes the intent.
    Returns: {"rewritten_query": str, "category": str}
    """
    llm = get_fallback_model() # Use faster model for routing
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        fast_llm = ChatGoogleGenerativeAI(model=llm, google_api_key=api_key, temperature=0)
    except:
        fast_llm = initialize_llm()
        
    mem_str = "\n".join([f"{m.get('role', 'user')}: {m.get('content', m.get('question', m.get('answer', '')))}" for m in (memory[-3:] if memory else [])])
    
    prompt = PromptTemplate.from_template(ANALYZER_PROMPT)
    chain = prompt | fast_llm
    
    try:
        res = chain.invoke({"question": question, "memory": mem_str})
        text = res.content
        # Extract JSON from potential markdown blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
            
        data = json.loads(text.strip())
        return {
            "rewritten_query": data.get("rewritten_query", question),
            "category": data.get("category", "General")
        }
    except Exception as e:
        logger.warning(f"Query analyzer failed, falling back: {e}")
        return {"rewritten_query": question, "category": "General"}

def compress_context(question: str, chunks: list) -> str:
    """
    LLM Context Compressor. Merges duplicates and removes noise.
    """
    if not chunks:
        return ""
        
    llm = get_fallback_model() # Use faster model
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        fast_llm = ChatGoogleGenerativeAI(model=llm, google_api_key=api_key, temperature=0)
    except:
        fast_llm = initialize_llm()
        
    chunks_str = "\n\n".join([f"--- CHUNK {i+1} ---\n{c.page_content}" for i, c in enumerate(chunks)])
    
    prompt = PromptTemplate.from_template(COMPRESSOR_PROMPT)
    chain = prompt | fast_llm
    
    try:
        res = chain.invoke({"question": question, "chunks": chunks_str})
        return res.content.strip()
    except Exception as e:
        logger.warning(f"Context compressor failed, falling back to raw: {e}")
        return "\n\n".join([c.page_content for c in chunks])
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import create_retriever_tool
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage

def get_agent_executor(retriever):
    """
    Initializes a LangChain Agent with tools and the production system prompt.
    """
    llm = initialize_llm()
    
    # 1. Retriever Tool
    retriever_tool = create_retriever_tool(
        retriever,
        "search_api_documentation",
        "Searches and returns excerpts from the API documentation. You MUST use this tool first to find relevant context for the user's question."
    )
    
    # 2. Calculator Tool
    def calculate(expression: str) -> str:
        try:
            return str(eval(expression, {"__builtins__": None}, {}))
        except Exception as e:
            return f"Error: {e}"
            
    calculator_tool = Tool.from_function(
        func=calculate,
        name="calculator",
        description="Useful for when you need to answer questions about math or rate limits."
    )
    
    tools = [retriever_tool, calculator_tool]
    
    # We use the QA_SYSTEM_PROMPT as the state modifier to enforce grounding and format
    agent_executor = create_react_agent(llm, tools, state_modifier=QA_SYSTEM_PROMPT)
    
    return agent_executor

def generate_answer(question: str, context: str, memory=None, retriever=None) -> str:
    """
    Generates an answer using a full LangChain Agent.
    Implements validation (len > 20), failover retries, and detailed telemetry.
    The 'context' argument is kept for signature compatibility but ignored, as the Agent handles retrieval.
    """
    start_time = time.time()
    
    if not retriever:
        yield "Vector database is not initialized. Please add documents."
        return

    # Format Memory and Context
    chat_history = []
    if memory:
        for m in memory[-3:]: # Include last 3 interactions
            chat_history.append(HumanMessage(content=m.get('question', '')))
            chat_history.append(SystemMessage(content=m.get('answer', '')))
            
    # Inject pre-retrieved context into the first message to force grounding
    initial_prompt = f"Retrieved Documentation Context:\n{context}\n\nUser Question: {question}"
            
    chain_input = {
        "messages": chat_history + [HumanMessage(content=initial_prompt)]
    }

    # Failover & Retry Execution
    max_retries = 2
    for attempt in range(max_retries):
        try:
            llm_start_time = time.time()
            agent_executor = get_agent_executor(retriever)
            
            full_response = ""
            for event in agent_executor.stream(chain_input, stream_mode="values"):
                # values mode returns the full state at each step
                message = event["messages"][-1]
                
                # If it's an AIMessage with tool calls
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tc in message.tool_calls:
                        yield f"🤔 *Thinking: Using {tc['name']}...*\n\n"
                        
                # If it's a final text response from AI (not a tool call)
                elif message.type == "ai" and message.content and not hasattr(message, "tool_calls"):
                    # We just yield the difference since stream_mode="values" gives the full content
                    chunk = message.content[len(full_response):]
                    if chunk:
                        full_response = message.content
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
            print(f"Model Used: {get_primary_model() if attempt == 0 else get_fallback_model()}")
            print("="*50 + "\n")
            
            return
            
        except Exception as e:
            logger.error(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                yield "An unexpected error occurred while generating the answer. Please ensure your API keys and quotas are valid, and try again."
