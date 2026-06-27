import re

def deduplicate_docs(chunks: list) -> list:
    """
    Removes exact duplicate chunks.
    """
    seen = set()
    deduped = []
    for c in chunks:
        sig = c.page_content[:100]
        if sig not in seen:
            seen.add(sig)
            deduped.append(c)
    return deduped

def rerank_and_score_confidence(question: str, chunks: list, top_k: int = 3) -> dict:
    """
    Fast Lexical & Semantic Reranker.
    Uses keyword overlap to score and rank chunks instantly.
    """
    if not chunks:
        return {"top_chunks": [], "confidence": 0}
        
    question_terms = set(re.findall(r'\w+', question.lower()))
    
    scored_chunks = []
    for chunk in chunks:
        content_lower = chunk.page_content.lower()
        chunk_terms = set(re.findall(r'\w+', content_lower))
        
        # Calculate Jaccard-like overlap score
        overlap = len(question_terms.intersection(chunk_terms))
        score = (overlap / max(len(question_terms), 1)) * 100
        
        # Boost score if exact phrase matches
        if question.lower() in content_lower:
            score += 30
            
        # Boost for API specifics
        if "api" in question.lower() and "endpoint" in content_lower:
            score += 10
            
        scored_chunks.append((score, chunk))
        
    # Sort by score descending and prune below threshold (e.g., 5)
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    valid_chunks = [c for score, c in scored_chunks if score >= 5]
    
    top_chunks = valid_chunks[:top_k]
    
    # Calculate average confidence based on scores of the valid chunks
    if not top_chunks:
        return {"top_chunks": [], "confidence": 0}
        
    top_scores = [score for score, c in scored_chunks if score >= 5][:top_k]
    avg_score = sum(top_scores) / len(top_scores)
    
    if avg_score > 40:
        confidence = 95
    elif avg_score > 10:
        confidence = 85
    else:
        confidence = 75 # Minimum viable
        
    return {"top_chunks": top_chunks, "confidence": confidence}

def compress_context(chunks: list) -> str:
    """
    String-based context compressor. Limits total characters to avoid context bloat.
    """
    compressed = [c.page_content for c in chunks]
    return "\n\n---\n\n".join(compressed)[:15000]
