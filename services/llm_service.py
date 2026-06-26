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

from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage

def get_agent_executor(retriever, memory_messages=None):
    """
    Initializes a LangChain Agent with tools.
    """
    api_key = get_google_api_key()
    model_name = get_primary_model()
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
        streaming=True
    )
    
    # 1. Retriever Tool
    retriever_tool = create_retriever_tool(
        retriever,
        "search_api_documentation",
        "Searches and returns excerpts from the API documentation. Always use this first."
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
    
    # Format Prompt
    agent_executor = create_react_agent(llm, tools, state_modifier=QA_SYSTEM_PROMPT)
    
    return agent_executor

def generate_answer(question: str, context: str, memory=None, retriever=None) -> str:
    """
    Generates an answer using the LangChain Agent.
    Streaming is handled by Streamlit's native callback or chunking.
    """
    try:
        if not retriever:
            yield "Vector database is not initialized. Please add documents."
            return
            
        agent_executor = get_agent_executor(retriever)
        
        chat_history = []
        if memory:
            for m in memory[-4:]:
                chat_history.append(HumanMessage(content=m['question']))
                chat_history.append(SystemMessage(content=m['answer']))
                
        # Stream response
        for chunk in agent_executor.stream(
            {"input": question, "chat_history": chat_history}
        ):
            if "actions" in chunk:
                for action in chunk["actions"]:
                    yield f"🤔 *Thinking: Using {action.tool}...*\n\n"
            elif "steps" in chunk:
                pass
            elif "output" in chunk:
                yield chunk["output"]
                
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        yield f"Gemini API quota exceeded or error occurred: {e}\nPlease try again later."
