import os
from config import get_google_api_key
from services.logging.logger import get_logger
from services.llm.provider_manager import ProviderManager

logger = get_logger("HealthCheck")

def run_health_checks(vector_store, retriever, total_docs):
    pm = ProviderManager()
    provider_health = pm.get_health_report()
    
    # We log the specific provider format as requested
    logger.info("Available Providers")
    if provider_health and isinstance(provider_health, dict):
        for provider, status in provider_health.items():
            logger.info(f"{provider} {status}")

    report = {
        "Embedding Model": "OK" if vector_store else "Failed",
        "Chroma": "OK" if vector_store else "Failed",
        "Documents": "OK" if total_docs > 0 else "Warning: 0",
        "Retriever": "OK" if retriever else "Failed",
        "LangGraph": "OK",
        "Disk": "OK" if os.access(".", os.W_OK) else "Read-Only"
    }
    
    # Add Providers to the report for the UI
    if provider_health and isinstance(provider_health, dict):
        for provider, status in provider_health.items():
            report[f"Provider {provider}"] = status
        
    status = "System Healthy"
    if "Failed" in report.values() or "Read-Only" in report.values():
        status = "System Degraded"
        
    logger.info(f"Health Check: {status}")
    return report, status
