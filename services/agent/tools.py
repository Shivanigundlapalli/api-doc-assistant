from services.logging.logger import get_logger, log_stage
from services.error_handler.handler import PipelineError

logger = get_logger("AgentTools")

def check_guardrails(question: str) -> bool:
    blocked_keywords = [
        "ignore previous instructions", "you are now a", "system prompt",
        "medical advice", "legal advice", "hack", "bypass", "exploit"
    ]
    question_lower = question.lower()
    for keyword in blocked_keywords:
        if keyword in question_lower:
            log_stage("Guardrails", "Blocked", {"keyword": keyword})
            return False
    log_stage("Guardrails", "Allowed")
    return True

def analyze_query(question: str, memory: list = None) -> dict:
    category = "General"
    question_lower = question.lower()
    
    if any(k in question_lower for k in ["auth", "token", "key", "secret", "oauth"]):
        category = "Authentication"
    elif any(k in question_lower for k in ["error", "400", "401", "404", "500", "fail", "bug"]):
        category = "Errors"
    elif any(k in question_lower for k in ["rate", "limit", "quota", "maximum", "exceed"]):
        category = "Rate Limits"
    elif any(k in question_lower for k in ["sdk", "python", "javascript", "curl"]):
        category = "SDK & Examples"
        
    rewritten_query = question
    if memory and len(question.split()) <= 3:
        last_q = memory[-1].get("question", "")
        if "key" in question_lower or "it" in question_lower:
            rewritten_query = f"{last_q} {question}"
            
    log_stage("Query Rewrite", "Success", {"original": question, "rewritten": rewritten_query, "category": category})
    return {"rewritten_query": rewritten_query, "category": category}
