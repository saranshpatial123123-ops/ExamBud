from backend.database.core import get_vector_store

def retrieve_chunks(query: str, k: int = 10, distance_threshold: float = 1.0, metadata_filter: dict = None) -> list[dict]:
    """
    Retrieve top k most relevant chunks from the vector database.
    Note: ChromaDB by default returns L2 squared distance where 0.0 means identical, 
    and larger values mean less similar. A reasonable threshold for "relevant" is < 1.0
    """
    vector_store = get_vector_store()
    
    # Standard similarity search with score (L2 distance from ChromaDB)
    # We pass the metadata_filter natively as a 'filter' kwarg to ChromaDB
    kwargs = {"k": k}
    if metadata_filter:
        kwargs["filter"] = metadata_filter
        
    results = vector_store.similarity_search_with_score(query, **kwargs)
    
    retrieved_chunks = []
    for doc, distance in results:
        # Distance filter (lower is better)
        if distance > distance_threshold:
            continue
            
        retrieved_chunks.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(distance)  # Lower is better
        })
        
    # Sort strictly by distance ascending (best match first)
    retrieved_chunks = sorted(retrieved_chunks, key=lambda x: x["score"])
    
    return retrieved_chunks
