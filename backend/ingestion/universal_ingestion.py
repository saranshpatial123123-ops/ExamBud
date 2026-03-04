import os
import mimetypes
from backend.ingestion.extractors import extract_text
from backend.tasks.video_tasks import process_lecture_video
from backend.ingestion.ingestion import process_file as process_document
from backend.processing.video_audio import extract_audio, transcribe_audio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from backend.config import settings
from backend.database.core import store_chunks
from backend.utils.file_utils import delete_file
from backend.utils.logging_utils import get_logger

logger = get_logger("UniversalIngestion")

def handle_audio_upload(file_path: str, metadata: dict):
    """Processes audio files into vector db"""
    # Use the same mechanism as video audio logic
    transcript = transcribe_audio(file_path)
    combined_text = "\n\n".join([seg["speech"] for seg in transcript])
    
    docs = [Document(page_content=combined_text, metadata=metadata)]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    split_docs = text_splitter.split_documents(docs)
    
    if not split_docs:
        logger.warning(f"Audio file {metadata.get('source_filename')} generated 0 split chunks.")
        return 0
        
    chunks = [doc.page_content for doc in split_docs]
    metadatas = []
    for i, doc in enumerate(split_docs):
        doc.metadata["chunk_index"] = i
        metadatas.append(doc.metadata)
        
    store_chunks(chunks, metadatas)
    delete_file(file_path)
    logger.info(f"Successfully processed audio {metadata.get('source_filename')}. Generated {len(chunks)} chunks.")
    return len(chunks)

def handle_universal_upload(background_tasks, file_path: str, filename: str, content_type: str, metadata: dict):
    """Routes files to correct ingestion strategies based on type"""
    
    # Guess mime if not provided cleanly by FastAPI
    if not content_type or content_type == "application/octet-stream":
        content_type, _ = mimetypes.guess_type(file_path)
    
    if not content_type:
        content_type = ""
        
    is_video = content_type.startswith("video/")
    is_audio = content_type.startswith("audio/")
    is_image = content_type.startswith("image/")
    
    logger.info(f"Received file '{filename}' with dynamically parsed MIME '{content_type}'.")
    
    if is_video:
        metadata["source_type"] = "video"
        logger.info(f"Dispatching video '{filename}' to BackgroundTasks queue.")
        background_tasks.add_task(process_lecture_video, file_path, metadata)
        return {"status": "success", "message": "Video is processing in background"}
        
    elif is_audio:
        metadata["source_type"] = "audio"
        logger.info(f"Dispatching audio '{filename}' to BackgroundTasks queue.")
        background_tasks.add_task(handle_audio_upload, file_path, metadata)
        return {"status": "success", "message": "Audio is processing in background"}
        
    else:
        # Documents, Texts, CSV, Image (OCR)
        # Using existing document logic but extending extractors underneath
        if is_image:
            metadata["source_type"] = "image"
        else:
            metadata["source_type"] = "document"
            
        logger.info(f"Routing '{filename}' to synchronous standard parse logic.")
        num_chunks = process_document(
            file_path, filename, content_type,
            institute=metadata.get("institute", ""),
            branch=metadata.get("branch", ""),
            semester=metadata.get("semester", ""),
            subject=metadata.get("subject", ""),
            topic=metadata.get("topic", None),
            lecture_number=metadata.get("lecture_number", None)
        )
        
        return {
            "status": "success",
            "message": "File synchronously processed",
            "chunks": num_chunks
        }
