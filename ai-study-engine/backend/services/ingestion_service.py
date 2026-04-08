from backend.ingestion.universal_ingestion import handle_universal_upload
from fastapi import BackgroundTasks

def handle_upload(background_tasks: BackgroundTasks, file_path: str, filename: str, content_type: str, metadata: dict):
    return handle_universal_upload(background_tasks, file_path, filename, content_type, metadata)
