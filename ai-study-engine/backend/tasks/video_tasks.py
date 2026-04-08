import os
import shutil
from backend.processing.video_audio import extract_audio, transcribe_audio
from backend.processing.video_vision import extract_frames, extract_slide_text
from backend.processing.video_merge import merge_transcript_and_visuals, format_embedding_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from backend.config import settings
from backend.database.core import store_chunks, is_file_ingested
from backend.utils.file_utils import delete_file
import hashlib

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_lecture_video(file_path: str, metadata: dict):
    """
    Background task to process a single uploaded video file completely asynchronously.
    """
    audio_path = None
    frame_dir = None
    try:
        # Step 0: Hash Deduplication Check
        file_hash = get_file_hash(file_path)
        if is_file_ingested(file_hash):
            print(f"Video {metadata.get('source_filename', 'Unknown')} is already ingested (Hash Match). Skipping.")
            return

        # Step 1: Audio Extraction & Transcription
        audio_path = extract_audio(file_path)
        transcript = transcribe_audio(audio_path)
        
        # Step 2: Frame Extraction & OCR
        frame_dir = os.path.join(settings.UPLOAD_DIR, "temp_frames")
        os.makedirs(frame_dir, exist_ok=True)
        frame_paths = extract_frames(file_path, frame_dir)
        visuals = extract_slide_text(frame_paths) # Note: this also eagerly deletes frames inside
        
        # Step 3: Merge and Format Text
        merged_chunks_raw = merge_transcript_and_visuals(transcript, visuals)
        
        docs = []
        for c in merged_chunks_raw:
            page_content = format_embedding_text(c)
            doc_meta = metadata.copy()
            doc_meta["timestamp"] = c.get("timestamp", "")
            doc_meta["speech_text"] = c.get("speech", "")
            doc_meta["slide_text"] = c.get("visual_text", "")
            docs.append(Document(page_content=page_content, metadata=doc_meta))
        
        # Step 4: Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        split_docs = text_splitter.split_documents(docs)
        
        if not split_docs:
            print(f"Skipping empty video processing for {file_path}")
            return
            
        # Step 5: Embeddings and Vector DB Storage
        chunks = [doc.page_content for doc in split_docs]
        metadatas = []
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_index"] = i
            doc.metadata["file_hash"] = file_hash
            metadatas.append(doc.metadata)
            
        store_chunks(chunks, metadatas)
        print(f"Successfully processed video {metadata.get('source_filename', 'Unknown')} into {len(chunks)} chunks.")
        
    except Exception as e:
        print(f"Error processing video {file_path}: {e}")
    finally:
        # Step 6: Cleanup original files to save space
        delete_file(file_path)
        if audio_path:
            delete_file(audio_path)
        try:
            if frame_dir and os.path.exists(frame_dir):
                shutil.rmtree(frame_dir)
        except OSError:
            pass
