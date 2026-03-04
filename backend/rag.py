from .config import settings
from .retrieval import retrieve_chunks

def get_llm():
    """
    Initializes the LLM. Falls back to a local HuggingFace model if OpenAI API Key is not set.
    """
    if settings.OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
    else:
        # Fallback to local HuggingFace pipeline for text generation. 
        # Using flan-t5-base as a lightweight instruction-following model.
        from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
        from transformers import pipeline
        
        pipe = pipeline(
            "text2text-generation", 
            model="google/flan-t5-base", 
            max_new_tokens=512,
            model_kwargs={"temperature": 0.0}
        )
        return HuggingFacePipeline(pipeline=pipe)

def condense_context(query: str, chunks: list, llm) -> str:
    """
    Condenses the raw retrieved chunks into a concise summary of only the relevant information.
    This improves answer quality by removing noise before final generation.
    """
    raw_text = "\n\n".join([f"[Source: {c['metadata'].get('source_filename', 'Unknown')}]\n{c['content']}" for c in chunks])
    
    prompt = f"""You are an expert study assistant.
Read the following raw extracts from study materials.
Extract and summarize ONLY the information that is helpful for answering the student's question: "{query}"
If none of the information is helpful, reply exactly with: "No relevant information found."

Raw Materials:
{raw_text}

Condensed Context:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return f"Context compression error: {str(e)}"

def generate_answer(query: str) -> dict:
    """
    1. Retrieve relevant chunks from the database
    2. Condense the context (Summarization)
    3. Construct the final RAG Prompt
    4. Generate the answer using the LLM
    """
    # Retrieve top 10 chunks, using distance_threshold parameter handled in retrieval.py (L2, lower is better)
    chunks = retrieve_chunks(query, k=10, distance_threshold=1.0)
    
    if not chunks:
        # Handled the case where no chunks passed the threshold
        return {
            "answer": "I couldn't find this in the uploaded materials.",
            "sources": []
        }
        
    llm = get_llm()
    
    # Context Compression Step
    condensed_context = condense_context(query, chunks, llm)
    
    # If the LLM determined there was no relevant information during compression
    if "no relevant information found" in condensed_context.lower():
        return {
            "answer": "I couldn't find this in the uploaded materials.",
            "sources": []
        }
        
    # Construct source metadata block for returning to user
    sources = []
    for chunk in chunks:
        sources.append({
            "source_filename": chunk["metadata"].get("source_filename", "Unknown"),
            "chunk_index": chunk["metadata"].get("chunk_index", -1),
            "score": chunk["score"],
            "chunk_text": chunk["content"]
        })
    
    # Final Generation 
    final_prompt = f"""You are an AI study tutor. Your task is to accurately answer the student's question based strictly on the provided condensed context materials.

Condensed Context Materials:
{condensed_context}

Student Question: {query}

Instructions:
- Only answer using the information in the provided context.
- Cite your sources where possible.
- If the answer is not present in the context materials, reply exactly with: "I could not find that in the uploaded materials" and do not attempt to guess or use outside knowledge.

Answer:"""

    try:
        response = llm.invoke(final_prompt)
        # Handle variations between ChatModels (returns AIMessage) and standard LLMs (returns string)
        answer = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
        
    return {
        "answer": answer.strip(),
        "sources": sources
    }
