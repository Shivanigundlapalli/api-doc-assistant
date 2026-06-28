import time
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from config import get_config
from services.logging.logger import get_logger, log_stage
from services.error_handler.handler import PipelineError

logger = get_logger("ProviderManager")

class ProviderManager:
    def __init__(self):
        self.providers = []
        self._initialize_providers()

    def _initialize_providers(self):
        """Initializes the provider list strictly in priority order, skipping those without keys."""
        google_key = get_config("GOOGLE_API_KEY")
        openai_key = get_config("OPENAI_API_KEY")
        
        # 1. Gemini 2.5 Flash
        if google_key and google_key != "YOUR_GEMINI_KEY_HERE":
            self.providers.append({
                "name": "Gemini 2.5 Flash",
                "init": lambda: ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=google_key, temperature=0)
            })
            
            # 2. Gemini 2.0 Flash
            self.providers.append({
                "name": "Gemini 2.0 Flash",
                "init": lambda: ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_key, temperature=0)
            })
            
        # 3. GPT-4.1 Mini (mapped to gpt-4o-mini)
        if openai_key and openai_key != "YOUR_OPENAI_KEY_HERE":
            self.providers.append({
                "name": "GPT-4.1 Mini (OpenAI)",
                "init": lambda: ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0)
            })
            
            # 4. GPT-4.1 Nano (mapped to gpt-4o-mini as fallback since nano doesn't exist explicitly via API)
            self.providers.append({
                "name": "GPT-4.1 Nano (OpenAI)",
                "init": lambda: ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0)
            })
            
        # 5. Local Ollama (Assuming it's configured if requested, no API key needed usually)
        ollama_url = get_config("OLLAMA_BASE_URL")
        # We add it as the final fallback
        self.providers.append({
            "name": "Local Ollama",
            "init": lambda: ChatOllama(model=get_config("OLLAMA_MODEL", "llama3.1"), base_url=ollama_url, temperature=0)
        })

    def get_health_report(self) -> dict:
        """Returns a dict of which providers are properly configured based on keys."""
        report = {
            "Gemini": "✓" if get_config("GOOGLE_API_KEY") else "✗",
            "OpenAI": "✓" if get_config("OPENAI_API_KEY") else "✗",
            "Ollama": "✓" if get_config("OLLAMA_BASE_URL") else "✗" # Simplistic check for Ollama explicit setup
        }
        # If no URL is provided, we can assume Ollama is local default if it responds, but for health check:
        if report["Ollama"] == "✗":
             # We assume Ollama is not explicitly enabled if URL is not set.
             pass
             
        return report

    def execute_with_failover(self, prompt_template, output_parser, inputs: dict):
        """
        Executes the LangChain with exponential backoff and automatic provider switching.
        Returns a completed string answer and the selected model name.
        """
        backoff_delays = [1, 2, 4]
        
        # Calculate prompt length for telemetry
        try:
            formatted_prompt = prompt_template.format(**inputs)
            prompt_len = len(formatted_prompt)
        except Exception:
            prompt_len = 0
            
        for provider in self.providers:
            model_name = provider["name"]
            model_init_fn = provider["init"]
            
            log_stage("LLM Routing", "Selected Provider", {"provider": model_name, "prompt_length": prompt_len})
            
            for attempt, delay in enumerate(backoff_delays + [0]):
                try:
                    llm = model_init_fn()
                    chain = prompt_template | llm | output_parser
                    
                    start_time = time.time()
                    
                    log_stage("LLM Generation", "Network Request Started", {"provider": model_name, "attempt": attempt + 1})
                    
                    iterator = chain.stream(inputs)
                    first_chunk = next(iterator, None)
                    
                    def safe_stream_generator():
                        full_res = ""
                        try:
                            if first_chunk:
                                full_res += first_chunk
                                yield first_chunk
                            for chunk in iterator:
                                full_res += chunk
                                yield chunk
                                
                            latency = time.time() - start_time
                            log_stage("LLM Generation", "Streaming Finished", {
                                "provider": model_name,
                                "latency": f"{latency:.2f}s",
                                "chars_produced": len(full_res),
                                "retries": attempt
                            })
                        except Exception as e:
                            import traceback
                            tb = traceback.format_exc()
                            logger.error(f"[{model_name}] Stream dropped unexpectedly:\n{tb}")
                            err = f"\n\n**Generation Error:** Stream dropped mid-way ({type(e).__name__}).\n```\n{e}\n```"
                            full_res += err
                            yield err
                            
                    return safe_stream_generator(), model_name
                    
                except Exception as e:
                    err_str = str(e).lower()
                    exc_type = type(e).__name__
                    
                    transient_errors = ["ReadError", "Timeout", "ConnectionResetError", "RemoteProtocolError", "ConnectError", "ReadTimeout"]
                    
                    if "quota" in err_str or "billing" in err_str or "insufficient_quota" in err_str or "exhausted" in err_str:
                        log_stage("LLM Failover", "Provider Switched", {"failed_provider": model_name, "reason": "API Quota Exceeded"})
                        st.toast(f"Skipping {model_name}: API quota exceeded.", icon="❌")
                        break # Move to next model IMMEDIATELY
                        
                    elif "429" in err_str or "503" in err_str or "500" in err_str or "timeout" in err_str or "rate limit" in err_str or exc_type in transient_errors:
                        if delay > 0:
                            logger.warning(f"[{model_name}] Temporary error. Retrying in {delay}s... ({exc_type})")
                            st.toast(f"AI service busy. Retrying automatically in {delay}s...", icon="🔄")
                            time.sleep(delay)
                            continue
                        else:
                            log_stage("LLM Failover", "Provider Switched", {"failed_provider": model_name, "reason": f"Retries exhausted ({exc_type})"})
                            st.toast(f"Switching AI model due to high traffic...", icon="⚠️")
                            break # Move to next model
                    else:
                        log_stage("LLM Failover", "Provider Switched", {"failed_provider": model_name, "reason": f"Fatal error: {type(e).__name__} - {e}"})
                        st.toast(f"Model failed, falling back to alternatives...", icon="⚠️")
                        break # Move to next model

        # Graceful Failure: All providers exhausted
        context = inputs.get("context", "No context available.")
        
        fallback_msg = (
            "## Direct Answer\n"
            "The AI generation service is temporarily unavailable due to high traffic or quota limits, but I successfully retrieved the exact documentation for your query.\n\n"
            "## Explanation\n"
            f"{context}\n\n"
            "## Notes\n"
            "AI service disruption (Rate Limits / Quota Exceeded). Rendering raw documentation instead.\n\n"
            "## Confidence\n"
            "Low (Raw Document Fallback)"
        )
                
        log_stage("LLM Failover", "Ultimate Fallback Triggered", {"reason": "All providers failed"})
        return fallback_msg, "Raw-Chunks-Fallback"
