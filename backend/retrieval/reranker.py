from sentence_transformers import CrossEncoder

# Global instance so we don't reload the model on every request
_reranker_model = None

def get_reranker():
    global _reranker_model
    if _reranker_model is None:
        # BAAI/bge-reranker-base is a widely used, highly effective cross-encoder
        _reranker_model = CrossEncoder('BAAI/bge-reranker-base', max_length=512)
    return _reranker_model

def rerank_chunks(query: str, chunks: list[dict], top_n: int = 5, threshold: float = 0.2) -> list[dict]:
    """
    Given a query and a list of candidate chunks (each a dict with 'content', 'metadata', etc.),
    use a Cross-Encoder to compute a relevance score for each (query, chunk) pair.
    Sort the chunks descending by score, filter by threshold, and return the top_n.
    """
    if not chunks:
        return []

    model = get_reranker()
    
    # Prepare pairings
    pairs = [[query, chunk["content"]] for chunk in chunks]
    
    # Compute scores
    scores = model.predict(pairs)
    
    valid_chunks = []
    # Assign scores back to chunks
    for chunk, score in zip(chunks, scores):
        chunk["reranking_score"] = float(score)
        # Apply strict threshold to drop weak chunks found by initial vector/BM25 retrieval
        if chunk["reranking_score"] >= threshold:
            valid_chunks.append(chunk)
            
    # Sort descending (higher reranker score is better)
    valid_chunks.sort(key=lambda x: x["reranking_score"], reverse=True)
    
    return valid_chunks[:top_n]
