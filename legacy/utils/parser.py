import re

def parse_enterprise_answer(markdown_text: str) -> dict:
    """
    Parses the strict Markdown response from the LLM into a structured dictionary
    so the UI can render it into custom components.
    """
    parsed = {
        "confidence": "",
        "quick_answer": "",
        "key_details": "",
        "code_example": "",
        "developer_actions": "",
        "edge_cases": "",
        "source_snippets": "",
        "sources_text": "",
        "related": "",
        "related_questions": "",
        "explanation": "" # Fallback
    }
    
    # Split the text by headers (handle ##, ###, ####)
    sections = re.split(r'(?m)^#{2,4}\s+', markdown_text)
    
    # The first split might be empty or preamble, so we iterate
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.split('\n', 1)
        # Normalize header: uppercase and replace spaces with underscores
        header = lines[0].strip().upper().replace(" ", "_")
        content = lines[1].strip() if len(lines) > 1 else ""
        
        if "CONFIDENCE" in header:
            parsed["confidence"] = content
        elif "QUICK_ANSWER" in header:
            parsed["quick_answer"] = content
        elif "KEY_DETAILS" in header:
            parsed["key_details"] = content
        elif "CODE_EXAMPLE" in header or "CODE" in header:
            parsed["code_example"] = content
        elif "DEVELOPER_ACTIONS" in header or "STEPS" in header:
            parsed["developer_actions"] = content
        elif "EDGE_CASES" in header or "WARNINGS" in header:
            parsed["edge_cases"] = content
        elif "SOURCE_SNIPPETS" in header:
            parsed["source_snippets"] = content
        elif "SOURCES" in header:
            parsed["sources_text"] = content
        elif "RELATED_DOCUMENTATION" in header or "RELATED" in header and "QUESTIONS" not in header:
            parsed["related"] = content
        elif "RELATED_QUESTIONS" in header:
            parsed["related_questions"] = content
        else:
            # If it's a completely unknown header, dump it into explanation
            parsed["explanation"] += f"\n\n**{header}**\n{content}"
            
    # Fallback: if parsing completely failed
    if not any([parsed["quick_answer"], parsed["key_details"], parsed["code_example"], parsed["developer_actions"], parsed["edge_cases"]]):
        parsed["explanation"] = markdown_text
        
    return parsed
