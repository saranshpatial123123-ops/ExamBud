import os
import json
import uuid
from datetime import datetime
from pydantic import BaseModel
from backend.config import settings
from backend.intelligence.mastery_engine import load_student_mastery, update_topic_mastery
from backend.retrieval.hybrid_retrieval import hybrid_retrieve
from backend.knowledge_graph.concept_graph import load_concept_graph
from backend.utils.llm_provider import get_llm
from langchain.prompts import PromptTemplate

def get_tutor_session_filepath(student_id: str, session_id: str) -> str:
    logs_dir = os.path.join(settings.BASE_DIR, "data", "tutor_sessions")
    os.makedirs(logs_dir, exist_ok=True)
    safe_id = "".join(c for c in student_id if c.isalnum() or c in ('_', '-', '.'))
    return os.path.join(logs_dir, f"{safe_id}_{session_id}.json")

def generate_tutor_session(student_id: str, institute: str, branch: str, semester: str, subject: str, topic: str) -> dict:
    """
    Starts a tutoring session. Uses hybrid retrieval to pull context, checks mastery,
    and uses an LLM to generate targeted teaching material and adaptive questions.
    """
    # 1. Load Mastery
    profile = load_student_mastery(student_id)
    topic_data = profile["topic_mastery"].get(topic.lower().strip(), {})
    mastery = topic_data.get("mastery", 0.0)
    
    difficulty = "basic"
    if mastery >= 0.7:
        difficulty = "advanced"
    elif mastery >= 0.4:
        difficulty = "intermediate"
        
    # 2. Retrieve Course Context
    metadata_filter = {
        "institute": institute.lower().strip(),
        "branch": branch.lower().strip(),
        "semester": semester.lower().strip(),
        "subject": subject.lower().strip()
    }
    retrieved_chunks = hybrid_retrieve(topic, metadata_filter, initial_k=15, final_k=3)
    context_text = "\n\n".join([chunk.get("content", "") for chunk in retrieved_chunks])
    
    # Prerequisite recovery check (Inform LLM to focus on basics if failing)
    prereq_warning = ""
    if mastery < 0.4:
        cg = load_concept_graph(institute, branch, semester, subject)
        prereqs = []
        for c in cg.get("concepts", []):
            if c.get("concept", "").lower().strip() == topic.lower().strip():
                prereqs = c.get("prerequisites", [])
                break
        if prereqs:
            prereq_warning = f"\nThe student is struggling (Mastery: {mastery}). Explicitly relate the explanation back to these prerequisites: {', '.join(prereqs)}."

    # 3. LLM Generation
    llm = get_llm()
    
    prompt = PromptTemplate(
        input_variables=["topic", "difficulty", "context", "prereq"],
        template="""
You are an expert AI tutor teaching a student about "{topic}".
The student requires "{difficulty}" level questions based on their past mastery.
{prereq}

Using ONLY the provided course material below, create a structured tutoring session.
If the material doesn't contain enough info, teach them exactly what is in the text and generate questions based only on that text.

Format your output STRICTLY as valid JSON with exactly this structure:
{{
    "explanation": "A clear, engaging explanation of the topic.",
    "example": "A concrete worked example or analogy.",
    "practice_questions": [
        {{
            "question_id": "q1",
            "question": "The question text here...",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A - The exact string of the correct option",
            "explanation": "Why this answer is correct."
        }},
        // Generate exactly 3 questions
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
        "prereq": prereq_warning
    })
    
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        session_data = json.loads(content)
        
        # Strip answers from payload before sending to client, store full data locally
        session_id = str(uuid.uuid4())
        
        full_session = {
            "session_id": session_id,
            "student_id": student_id,
            "topic": topic,
            "mastery_before": mastery,
            "timestamp": datetime.now().isoformat(),
            "llm_payload": session_data
        }
        
        filepath = get_tutor_session_filepath(student_id, session_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(full_session, f, indent=2)
            
        # Clean the object for the student (hide answers)
        student_view = {
            "session_id": session_id,
            "topic": topic,
            "explanation": session_data["explanation"],
            "example": session_data["example"],
            "practice_questions": [
                {
                    "question_id": q["question_id"],
                    "question": q["question"],
                    "options": q["options"]
                } for q in session_data["practice_questions"]
            ]
        }
        return student_view
        
    except Exception as e:
        raise ValueError(f"Failed to generate tutoring session: {str(e)}")

def evaluate_tutor_answers(student_id: str, session_id: str, topic: str, student_answers: list) -> dict:
    """
    Evaluates submitted answers against the stored session, updates mastery, and calculates feedback.
    student_answers format: [{"question_id": "q1", "answer": "Option A"}, ...]
    """
    filepath = get_tutor_session_filepath(student_id, session_id)
    if not os.path.exists(filepath):
        raise ValueError("Tutor session not found or expired.")
        
    with open(filepath, "r", encoding="utf-8") as f:
        session = json.load(f)
        
    if session.get("evaluated"):
        raise ValueError("This session has already been evaluated.")
        
    questions = session["llm_payload"]["practice_questions"]
    q_map = {q["question_id"]: q for q in questions}
    
    correct_count = 0
    feedback_list = []
    
    for ans in student_answers:
        q_id = ans.get("question_id")
        user_choice = ans.get("answer")
        
        if q_id in q_map:
            actual = q_map[q_id]
            is_correct = str(user_choice).lower().strip() == str(actual["correct_answer"]).lower().strip()
            if is_correct:
                correct_count += 1
                
            feedback_list.append({
                "question_id": q_id,
                "is_correct": is_correct,
                "correct_answer": actual["correct_answer"],
                "explanation": actual["explanation"]
            })
            
    total_q = len(questions)
    accuracy = correct_count / total_q if total_q > 0 else 0.0
    
    # 3. Update Mastery Tracking
    # Assumes average 2 mins per question for proxy time_taken
    time_taken_proxy = total_q * 120 
    
    new_topic_data = update_topic_mastery(
        student_id=student_id,
        topic=topic,
        accuracy=accuracy,
        time_taken=time_taken_proxy,
        attempts=1
    )
    
    # 4. Save Evaluation State
    session["evaluated"] = True
    session["correct"] = correct_count
    session["total_questions"] = total_q
    session["mastery_after"] = new_topic_data["mastery"]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
        
    return {
        "status": "success",
        "score": f"{correct_count}/{total_q}",
        "accuracy": accuracy,
        "mastery_before": session["mastery_before"],
        "mastery_after": session["mastery_after"],
        "feedback": feedback_list
    }
