from langchain_community.embeddings import HuggingFaceEmbeddings
from backend.config import settings

def get_embeddings_model():
    """
    Returns the configured embedding model.
    Using a local HuggingFace embedding model (all-MiniLM-L6-v2) by default 
    so the system runs out-of-the-box without OpenAI API keys.
    Can easily be switched to OpenAIEmbeddings if OPENAI_API_KEY is provided.
    """
    # If using OpenAI:
    # from langchain_openai import OpenAIEmbeddings
    # return OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
