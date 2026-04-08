from backend.database.core import get_vector_store
from backend.retrieval.retrieval import retrieve_chunks as vector_retrieve
from rank_bm25 import BM25Okapi
from backend.retrieval.query_rewriter import rewrite_query
from backend.retrieval.reranker import rerank_chunks
from backend.utils.logging_utils import get_logger

logger = get_logger("HybridRetrieval")

# Simple in-memory cache mapping course_id string to a tuple of (BM25Okapi_instance, documents_list, metadatas_list)
# In a robust production setup, consider Redis or periodic pre-computation processes.
_bm25_cache = {}

def get_bm25_results(query: str, metadata_filter: dict, k: int = 10) -> list[dict]:
    """
    Performs BM25 keyword search over chunks matching the given metadata filter.
    Caches the BM25 index per course scope to avoid re-tokenizing thousands of chunks.
    """
    course_id = "global"
    if metadata_filter:
        # Create a stable, sorted string key for caching
        course_id = "_".join(f"{k}-{v}" for k, v in sorted(metadata_filter.items()))
        
    if course_id not in _bm25_cache:
        vector_store = get_vector_store()
        
        kwargs = {"include": ["documents", "metadatas"]}
        if metadata_filter:
            from backend.database.core import build_chroma_filter
            kwargs["where"] = build_chroma_filter(metadata_filter)
            
        results = vector_store.get(**kwargs)
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        if not documents:
            return []
            
        # Tokenize and instantiate index
        tokenized_corpus = [doc.lower().split() for doc in documents]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Cache for future queries against this course
        _bm25_cache[course_id] = (bm25, documents, metadatas)
        
    bm25, documents, metadatas = _bm25_cache[course_id]
    
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Get top k indices
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    
    bm25_chunks = []
    for idx in top_indices:
        if scores[idx] > 0: # Only return if there's actual keyword overlap
            bm25_chunks.append({
                "content": documents[idx],
                "metadata": metadatas[idx],
                "score": float(scores[idx]), # Note: BM25 score semantics are different from Vector L2 distance
                "source_type": "bm25"
            })
            
    return bm25_chunks

def hybrid_retrieve(original_query: str, metadata_filter: dict = None, initial_k: int = 20, final_k: int = 5) -> list[dict]:
    """
    1. Rewrite Query
    2. Run Vector Search + BM25 Search
    3. Merge Results
    4. Rerank
    """
    # 1. Expand query
    queries = rewrite_query(original_query)
    logger.info(f"Query Rewrite expanded '{original_query}' into {len(queries)} sub-queries.")
    
    # 2. Run searches
    all_chunks = {}
    
    for q in queries:
        # Vector search (fetches up to initial_k)
        # Using a relaxed distance_threshold to capture more candidates for the reranker
        v_results = vector_retrieve(q, k=initial_k, distance_threshold=1.5, metadata_filter=metadata_filter)
        
        for ch in v_results:
            # Create a unique key using filename, chunk index, or content hash to deduplicate
            key = f"{ch['metadata'].get('source_filename', '')}_{ch['metadata'].get('chunk_index', '')}"
            if not key or key == "_":
                key = hash(ch['content'])
                
            if key not in all_chunks:
                ch["source_type"] = "vector"
                all_chunks[key] = ch
                
        # BM25 search
        b_results = get_bm25_results(q, metadata_filter=metadata_filter, k=initial_k)
        for ch in b_results:
            key = f"{ch['metadata'].get('source_filename', '')}_{ch['metadata'].get('chunk_index', '')}"
            if not key or key == "_":
                key = hash(ch['content'])
                
            if key not in all_chunks:
                all_chunks[key] = ch
            else:
                all_chunks[key]["source_type"] = "hybrid" # Found in both

    merged_results = list(all_chunks.values())
    logger.info(f"Pre-rerank vector/BM25 overlap yielded {len(merged_results)} unique context chunks.")
    
    # 4. Rerank
    # The reranker needs the ORIGINAL user query to accurately judge semantic relevance
    # because expanded queries might introduce drift.
    best_chunks = rerank_chunks(original_query, merged_results, top_n=final_k)
    logger.info(f"Reranker extracted {len(best_chunks)} optimal target chunks from the merge payload.")
    
    return best_chunks
