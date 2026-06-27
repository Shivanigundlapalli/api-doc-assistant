from langchain_core.prompts import PromptTemplate
from prompts.system_prompts import QA_SYSTEM_PROMPT

def build_qa_prompt(question: str, context: str, memory: list = None) -> PromptTemplate:
    """
    Builds the main QA prompt using the Production Backend Prompt template.
    """
    chat_history = ""
    if memory:
        chat_history = "\n".join([f"User: {m.get('question', '')}\nAssistant: {m.get('answer', '')}" for m in memory[-3:]])
        
    prompt = PromptTemplate.from_template(
        QA_SYSTEM_PROMPT + "\n\n"
        "--- CONVERSATION HISTORY ---\n{chat_history}\n\n"
        "--- RETRIEVED DOCUMENTATION ---\n{context}\n\n"
        "User Question: {question}"
    )
    
    return prompt
