from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.ingestion.extractors import extract_text
from backend.database.core import store_chunks, is_file_ingested
from backend.config import settings
import hashlib

def get_file_hash(file_path: str) -> str:
    """Generates a SHA-256 hash of the file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in chunks to efficiently handle large files
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def process_file(
    file_path: str, filename: str, file_type: str, 
    institute: str = "", branch: str = "", semester: str = "", subject: str = "",
    topic: str = None, lecture_number: int = None
) -> int:
    """
    Orchestrates the material ingestion pipeline:
    1. Check if file is already ingested via hash
    2. Extract text
    3. Split into chunks
    4. Generate metadata with normalized course scopes
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

    # 4. Create metadata (source, chunk index, file hash, and normalized course scopes)
    norm_institute = institute.strip().lower() if institute else ""
    norm_branch = branch.strip().lower() if branch else ""
    norm_semester = semester.strip().lower() if semester else ""
    norm_subject = subject.strip().lower() if subject else ""

    metadatas = []
    for i in range(len(chunks)):
        meta = {
            "source_filename": filename, 
            "chunk_index": i, 
            "file_hash": file_hash,
            "institute": norm_institute,
            "branch": norm_branch,
            "semester": norm_semester,
            "subject": norm_subject
        }
        if topic:
            meta["topic"] = topic.strip().lower()
        if lecture_number is not None:
            meta["lecture_number"] = lecture_number
            
        metadatas.append(meta)

    
    # 5. Store in vector database
    store_chunks(chunks, metadatas)
    
    return len(chunks)
