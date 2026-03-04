from langchain_community.vectorstores import Chroma
from backend.embeddings.embeddings import get_embeddings_model
from backend.config import settings

def get_vector_store() -> Chroma:
    """
    Initializes and returns the Chroma vector store.
    """
    embeddings = get_embeddings_model()
    vector_store = Chroma(
        collection_name="study_materials",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_DB_DIR
    )
    return vector_store

def store_chunks(chunks: list[str], metadatas: list[dict]):
    """
    Adds chunks of text and their associated metadata to the vector database.
    """
    vector_store = get_vector_store()
    vector_store.add_texts(texts=chunks, metadatas=metadatas)

def is_file_ingested(file_hash: str) -> bool:
    """
    Checks if a file has already been ingested by looking for its hash in metadata.
    """
    vector_store = get_vector_store()
    results = vector_store.get(where={"file_hash": file_hash})
    return len(results.get("ids", [])) > 0

def get_all_documents() -> dict:
    """
    Retrieves all documents stored in the vector database for debugging.
    """
    vector_store = get_vector_store()
    return vector_store.get()

def get_unique_metadata(field_name: str, filters: dict = None) -> list[str]:
    """
    Retrieves unique values for a specific metadata field, optionally constrained by other filters.
    Used for building directory browsing endpoints.
    """
    vector_store = get_vector_store()
    kwargs = {"include": ["metadatas"]}
    if filters:
        kwargs["where"] = filters
        
    results = vector_store.get(**kwargs)
    
    unique_vals = set()
    for meta in results.get("metadatas", []):
        if field_name in meta and meta[field_name]:
            unique_vals.add(meta[field_name])
            
    return sorted(list(unique_vals))

def get_chunks_by_metadata(filters: dict) -> list[str]:
    """
    Retrieves all document chunks that match the given metadata filters.
    Used for syllabus reconstruction and topic graphing.
    """
    vector_store = get_vector_store()
    results = vector_store.get(where=filters, include=["documents"])
    return results.get("documents", [])
