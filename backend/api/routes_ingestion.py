import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from backend.config import settings
from backend.utils.file_utils import save_upload_file
from backend.services.ingestion_service import handle_upload
from typing import Optional

router = APIRouter(tags=["Universal Ingestion"])

@router.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    institute: str = Form(...),
    branch: str = Form(...),
    semester: str = Form(...),
    subject: str = Form(...),
    topic: Optional[str] = Form(None),
    lecture_number: Optional[int] = Form(None)
):
    """
    Ingests almost any academic file type (documents, images, audio, video) into ChromaDB.
    """
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    try:
        save_upload_file(file, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    metadata = {
        "institute": institute.strip().lower(),
        "branch": branch.strip().lower(),
        "semester": semester.strip().lower(),
        "subject": subject.strip().lower(),
        "source_filename": file.filename
    }
    
    if topic:
        metadata["topic"] = topic.strip().lower()
    if lecture_number is not None:
        metadata["lecture_number"] = lecture_number

    try:
        result = handle_upload(background_tasks, file_path, file.filename, file.content_type, metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
