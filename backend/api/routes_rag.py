from fastapi import APIRouter, HTTPException
from backend.models.request_models import QueryRequest
from backend.services.rag_service import process_query, get_all_stored_documents

router = APIRouter(tags=["RAG & Retrieval"])

@router.get("/documents")
def get_documents_endpoint():
    """Debugging endpoint to inspect stored chunks."""
    try:
        return get_all_stored_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

@router.post("/query")
async def query_documents_endpoint(request: QueryRequest):
    """
    Search the vector database and answer the user's question using RAG.
    """
    filters = {}
    if request.institute:
        filters["institute"] = request.institute.strip().lower()
    if request.branch:
        filters["branch"] = request.branch.strip().lower()
    if request.semester:
        filters["semester"] = request.semester.strip().lower()
    if request.subject:
        filters["subject"] = request.subject.strip().lower()

    try:
        return process_query(request.question, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")
