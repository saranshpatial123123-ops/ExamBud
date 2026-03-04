from backend.rag.rag import get_llm

def rewrite_query(original_query: str, max_rewrites: int = 2) -> list[str]:
    """
    Uses an LLM to rewrite and expand the user's query into multiple queries 
    to improve retrieval recall.
    Returns a list of queries starting with the original query.
    Capped to `max_rewrites` to prevent runaway token use.
    """
    llm = get_llm()
    
    prompt = f"""You are an expert search assistant. Your task is to generate {max_rewrites} alternative variations of the given user query to improve document retrieval from a study materials database.
Do not answer the query. Just provide {max_rewrites} alternative queries that use synonyms and expanded terminology.
Output exactly one query per line.

Original Query: {original_query}

Alternative Queries:"""

    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        # Split by newlines and clean up
        variants = [original_query]
        for line in content.split("\n"):
            clean_line = line.strip().strip("-").strip("1234567890. ").strip()
            if clean_line and clean_line.lower() != original_query.lower() and clean_line != "Alternative Queries:":
                variants.append(clean_line)
                
        # Strict limit to original query + max_rewrites
        return variants[:max_rewrites + 1]
    except Exception as e:
        # Fallback to just the original query if rewriting fails
        print(f"Query rewriting failed: {e}")
        return [original_query]
