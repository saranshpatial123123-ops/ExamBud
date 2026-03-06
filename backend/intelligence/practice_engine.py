import json
from backend.retrieval.hybrid_retrieval import hybrid_retrieve
from backend.intelligence.difficulty_controller import compute_tutor_difficulty
from backend.utils.llm_provider import get_llm
from langchain.prompts import PromptTemplate

def generate_practice_set(student_id: str, institute: str, branch: str, semester: str, subject: str, topic: str, count: int = 5) -> dict:
    """
    Generates structured, mixed-format practice questions on demand using RAG context.
    Adapts strictly to the student's mastery of the requested topic.
    """
    difficulty = compute_tutor_difficulty(student_id, topic)
    
    metadata_filter = {
        "institute": institute.lower().strip(),
        "branch": branch.lower().strip(),
        "semester": semester.lower().strip(),
        "subject": subject.lower().strip()
    }
    
    retrieved_chunks = hybrid_retrieve(topic, metadata_filter, initial_k=20, final_k=4)
    if not retrieved_chunks:
        raise ValueError("No course data found to generate practice questions.")
        
    context_text = "\n\n".join([chunk.get("content", "") for chunk in retrieved_chunks])
    
    llm = get_llm()
    
    prompt = PromptTemplate(
        input_variables=["topic", "difficulty", "context", "count"],
        template="""
You are an expert examiner. Generate exactly {count} practice questions about "{topic}".
The difficulty must be "{difficulty}".

Include a mix of formats: "mcq", "short_answer", and "concept_check".
For MCQ, provide "options". For others, leave "options" as an empty array.

Output STRICTLY as valid JSON with exactly this structure:
{{
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "questions": [
        {{
            "question_id": "q1",
            "type": "mcq",
            "concept_tags": ["mutual_exclusion", "circular_wait"],
            "question": "The question text...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Why it's correct."
        }}
    ]
}}

Course Material:
{context}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "topic": topic,
        "difficulty": difficulty,
        "context": context_text,
        "count": count
    })
    
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        practice_data = json.loads(content)
        return practice_data
    except Exception as e:
        raise ValueError(f"Failed to generate practice set: {str(e)}")
