import json
import os
from backend.config import settings
from backend.database.core import get_chunks_by_metadata
from backend.utils.llm_provider import get_llm

def generate_topic_graph(institute: str, branch: str, semester: str, subject: str) -> dict:
    """
    1. Retrieves all text chunks belonging to a specific course scope.
    2. Combines logical sections.
    3. Uses an LLM to extract JSON topic graphs.
    4. Saves the generated graph locally for future syllabus tasks.
    """
    filters = {
        "institute": institute.lower().strip(),
        "branch": branch.lower().strip(),
        "semester": semester.lower().strip(),
        "subject": subject.lower().strip()
    }
    
    chunks = get_chunks_by_metadata(filters)
    
    if not chunks:
        raise ValueError("No materials found for this course scope.")
        
    # Combine the text chunks
    # To prevent blowing up the context window for large courses, 
    # we dynamically cap the total length passed to the summarizer in this module.
    # Advanced logic might chunk-and-map-reduce this, but we'll use a direct prompt for now.
    combined_text = "\n\n".join(chunks)
    max_chars = 30000  # Approx ~6-8k tokens depending on the tokenizer
    if len(combined_text) > max_chars:
        combined_text = combined_text[:max_chars]
        
    prompt = f"""You are an expert curriculum developer and AI Study Tutor.
Analyze the following raw course materials and extract a comprehensive, structured course syllabus.
Identify the main topics, subtopics, and key concepts.

Output strictly valid JSON with no conversational text, no markdown block quotes, and no formatting outside the raw JSON.
The structure MUST match this exact format:
{{
  "subject": "{filters['subject']}",
  "topics": [
    {{
      "name": "Topic Name",
      "subtopics": [
        "Subtopic 1",
        "Subtopic 2",
        "Subtopic 3"
      ]
    }}
  ]
}}

Course Materials:
{combined_text}
"""
    
    llm = get_llm()
    try:
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        # Strip potential markdown code blocks returned by LLMs
        answer = answer.strip()
        if answer.startswith("```json"):
            answer = answer[7:]
        elif answer.startswith("```"):
            answer = answer[3:]
            
        if answer.endswith("```"):
            answer = answer[:-3]
            
        answer = answer.strip()
        
        parsed_json = json.loads(answer)
    except json.JSONDecodeError:
        # Fallback if LLM output fails standard parsing
        parsed_json = {
            "subject": filters["subject"],
            "topics": [],
            "error": "LLM did not return valid JSON.",
            "raw_output": answer if 'answer' in locals() else "Unknown error."
        }
    except Exception as e:
        raise RuntimeError(f"Failed to generate topic graph: {str(e)}")
        
    # Persist the output
    graphs_dir = os.path.join(settings.BASE_DIR, "data", "topic_graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    # Safe filename
    filename = f"{filters['institute']}_{filters['branch']}_{filters['semester']}_{filters['subject']}.json"
    filename = "".join(c for c in filename if c.isalnum() or c in ('_', '.', '-'))
    
    filepath = os.path.join(graphs_dir, filename)
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(parsed_json, f, indent=2)
        
    return parsed_json

def load_topic_graph(institute: str, branch: str, semester: str, subject: str) -> dict:
    # Stub added to resolve missing import error
    return {"message": "Not implemented yet"}
