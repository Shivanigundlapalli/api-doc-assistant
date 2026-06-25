import re

def parse_enterprise_answer(markdown_text: str) -> dict:
    """
    Parses the strict Markdown response from the LLM into a structured dictionary
    so the UI can render it into custom components.
    """
    parsed = {
        "confidence": "",
        "quick_answer": "",
        "explanation": "",
        "steps": "",
        "code": "",
        "warnings": "",
        "related": ""
    }
    
    # Split the text by headers
    sections = re.split(r'(?m)^###\s+', markdown_text)
    
    # The first split might be empty or preamble, so we iterate
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.split('\n', 1)
        header = lines[0].strip().upper()
        content = lines[1].strip() if len(lines) > 1 else ""
        
        if "CONFIDENCE" in header:
            parsed["confidence"] = content
        elif "QUICK_ANSWER" in header:
            parsed["quick_answer"] = content
        elif "EXPLANATION" in header:
            parsed["explanation"] = content
        elif "STEPS" in header:
            parsed["steps"] = content
        elif "CODE" in header:
            parsed["code"] = content
        elif "WARNINGS" in header:
            parsed["warnings"] = content
        elif "RELATED" in header:
            parsed["related"] = content
            
    # Fallback: if parsing completely failed, dump it all into explanation
    if not any(parsed.values()):
        parsed["explanation"] = markdown_text
        
    return parsed
