from langchain.text_splitter import RecursiveCharacterTextSplitter
from .extractors import extract_text
from .database import store_chunks, is_file_ingested
from .config import settings
import hashlib

def get_file_hash(file_path: str) -> str:
    """Generates a SHA-256 hash of the file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to efficiently handle large files
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_file(file_path: str, filename: str, file_type: str) -> int:
    """
    Orchestrates the material ingestion pipeline:
    1. Check if file is already ingested via hash
    2. Extract text
    3. Split into chunks
    4. Generate metadata
    5. Store in vector db
    """
    # 1. Check if already ingested using file hash
    file_hash = get_file_hash(file_path)
    if is_file_ingested(file_hash):
        return -1  # Indicates already ingested

    # 2. Extract text based on file type
    text = extract_text(file_path, file_type)
    
    # 3. Chunk text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = text_splitter.split_text(text)
    
    if not chunks:
        return 0

    # 4. Create metadata (source filename, chunk index, and file hash)
    metadatas = [{"source_filename": filename, "chunk_index": i, "file_hash": file_hash} for i in range(len(chunks))]
    
    # 5. Store in vector database
    store_chunks(chunks, metadatas)
    
    return len(chunks)
