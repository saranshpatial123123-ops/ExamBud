from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from .config import settings
from .ingestion import process_file
from .database import get_all_documents

app = FastAPI(
    title="Material Ingestion and Knowledge Base API",
    description="API for ingesting PDF and PPTX files into a vector database for an AI Study Engine.",
    version="1.0.0"
)

# Supported MIME types
ALLOWED_TYPES = {
    "application/pdf": "PDF",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PPTX"
}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document (PDF or PPTX), extract text, chunk it, and store in the vector db.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type '{file.content_type}'. Only PDF and PPTX are allowed."
        )
    
    # Save file locally
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    try:
        # Process and ingest
        num_chunks = process_file(file_path, file.filename, file.content_type)
        if num_chunks == -1:
            return {
                "status": "skipped",
                "message": "File has already been ingested.",
                "filename": file.filename
            }
            
        return {
            "status": "success",
            "message": "File successfully uploaded and processed.",
            "filename": file.filename,
            "chunks_stored": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.get("/documents")
def get_documents():
    """Debugging endpoint to inspect stored chunks."""
    try:
        return get_all_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_documents(request: QueryRequest):
    """
    Search the vector database and answer the user's question using RAG.
    """
    try:
        from .rag import generate_answer
        return generate_answer(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

# Add a simple health check route
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
