from backend.rag.rag import generate_answer
from backend.database.core import get_all_documents

def process_query(question: str, filters: dict) -> str:
    metadata_filter = filters if filters else None
    return generate_answer(question, metadata_filter=metadata_filter)

def get_all_stored_documents():
    return get_all_documents()
