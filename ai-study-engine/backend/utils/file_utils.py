import os
from fastapi import UploadFile, HTTPException
from backend.config import settings

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Saves an UploadFile to the destination path while strictly enforcing the size limit."""
    try:
        total_size = 0
        with open(destination, "wb") as buffer:
            # Read in safe 1MB chunks to evaluate streaming size
            while chunk := upload_file.file.read(1024 * 1024):
                total_size += len(chunk)
                if total_size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413, 
                        detail=f"File exceeds maximum allowed upload size of {settings.MAX_UPLOAD_SIZE / (1024*1024*1024)}GB."
                    )
                buffer.write(chunk)
        return destination
    except Exception as e:
        # Prevent partial orphaned files on disk if connection drops or limit exceeded
        delete_file(destination)
        raise e
    finally:
        upload_file.file.close()

def delete_file(file_path: str):
    """Deletes a file if it exists."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
