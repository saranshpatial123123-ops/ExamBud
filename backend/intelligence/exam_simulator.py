import json
import uuid
import random
from datetime import datetime
from pydantic import BaseModel
from backend.config import settings
from backend.intelligence.mastery_engine import load_student_mastery
from backend.retrieval.hybrid_retrieval import hybrid_retrieve
from backend.knowledge_graph.topic_graph import load_topic_graph
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

def generate_exam(student_id: str, institute: str, branch: str, semester: str, subject: str, exam_duration: int, question_count: int) -> dict:
    """
    Simulates a full-course mock exam drawing from all topics.
    Dynamically balances difficulty using historic mastery analytics.
    """
    # 1. Topic Selection
    topic_graph = load_topic_graph(institute, branch, semester, subject)
    topics = [t.get("name") for t in topic_graph.get("topics", []) if t.get("name")]
    
    if not topics:
        raise ValueError("Cannot simulate an exam without a generated Topic Graph for the course.")
        
    # We want a mix of weak topics and random coverage
    profile = load_student_mastery(student_id)
    topic_mastery = profile.get("topic_mastery", {})
    
    weak_topics = []
    strong_topics = []
    for t_raw in topics:
        t = t_raw.lower().strip()
        m = topic_mastery.get(t, {}).get("mastery", 0.0)
        if m < 0.5:
            weak_topics.append(t_raw)
        else:
            strong_topics.append(t_raw)
            
    # Oversample weak topics for the exam to push the student
    selected_topics = []
    while len(selected_topics) < question_count:
        if weak_topics and random.random() < 0.6:
            selected_topics.append(random.choice(weak_topics))
        elif strong_topics:
            selected_topics.append(random.choice(strong_topics))
        else:
            selected_topics.append(random.choice(topics))
            
    # 2. Context Aggregation
    metadata_filter = {
        "institute": institute.lower().strip(),
        "branch": branch.lower().strip(),
        "semester": semester.lower().strip(),
        "subject": subject.lower().strip()
    }
    
    # We pull a broad conceptual chunk range across the course rather than micro-looping RAG per question
    retrieved_chunks = hybrid_retrieve(f"Core concepts of {subject}", metadata_filter, initial_k=30, final_k=10)
    context_text = "\n\n".join([chunk["chunk_text"] for chunk in retrieved_chunks])
    
    if len(context_text) > 15000:
        context_text = context_text[:15000]
        
    topics_str = ", ".join(list(set(selected_topics)))
    
    # 3. LLM Generation
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
    
    prompt = PromptTemplate(
        input_variables=["subject", "count", "topics", "context"],
        template="""
You are an expert university professor creating a final exam for "{subject}".
You must generate exactly {count} rigorous multiple-choice questions.

Ensure the questions heavily test these specific topics: {topics}.
Vary the difficulty from intermediate to advanced.

Output strictly as a JSON object:
{{
    "exam_title": "{subject} Mock Exam",
    "questions": [
        {{
            "question_id": "eq1",
            "topic_tested": "The specific topic this tests",
            "concept_tags": ["threads", "context_switch"],
            "question": "The exam question...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Why this is correct."
        }}
    ]
}}

Course Material context to draw facts from:
{context}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "subject": subject,
        "count": question_count,
        "topics": topics_str,
        "context": context_text
    })
    
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        exam_data = json.loads(content)
        
        # Save exact exam key
        exam_id = str(uuid.uuid4())
        exam_data["exam_id"] = exam_id
        exam_data["duration_minutes"] = exam_duration
        
        # We don't save full persistence right now as standard request, but it outputs immediately.
        # Format for client (strip answers)
        client_exam = {
            "exam_id": exam_id,
            "exam_title": exam_data["exam_title"],
            "duration_minutes": exam_duration,
            "questions": [
                {
                    "question_id": q["question_id"],
                    "question": q["question"],
                    "options": q["options"]
                } for q in exam_data["questions"]
            ],
            "answer_key": exam_data["questions"] # Passing back full key for stateless client eval in this MVP
        }
        
        return client_exam
    except Exception as e:
        raise ValueError(f"Failed to generate exam: {str(e)}")

def evaluate_exam(student_id: str, subject: str, student_answers: list, answer_key: list) -> dict:
    """ Evaluates the mock exam, calculates global readiness score, and dynamically updates concept mastery. """
    from backend.learning_state.concept_mastery_tracker import ConceptMasteryTracker
    
    key_map = {q["question_id"]: q for q in answer_key}
    
    correct_count = 0
    feedback = []
    topic_performance = {}
    
    for ans in student_answers:
        q_id = ans.get("question_id")
        user_choice = ans.get("answer")
        
        if q_id in key_map:
            actual = key_map[q_id]
            topic = actual.get("topic_tested", "General")
            
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
                
            topic_performance[topic]["total"] += 1
            
            is_correct = str(user_choice).lower().strip() == str(actual["correct_answer"]).lower().strip()
            if is_correct:
                correct_count += 1
                topic_performance[topic]["correct"] += 1
                
            # Automatically push Concept Mastery Deltas
            concept_tags = actual.get("concept_tags", [])
            for c_tag in concept_tags:
                ConceptMasteryTracker.update_mastery(student_id, c_tag, is_correct)
                
            feedback.append({
                "question_id": q_id,
                "is_correct": is_correct,
                "correct_answer": actual["correct_answer"],
                "explanation": actual["explanation"]
            })
            
    total_q = len(answer_key)
    exam_readiness = correct_count / total_q if total_q > 0 else 0.0
    
    weak_topics = []
    strong_topics = []
    
    for t, perf in topic_performance.items():
        acc = perf["correct"] / perf["total"] if perf["total"] > 0 else 0.0
        if acc < 0.5:
            weak_topics.append(t)
        else:
            strong_topics.append(t)
            
    return {
        "exam_readiness": exam_readiness,
        "score_string": f"{correct_count}/{total_q}",
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "detailed_feedback": feedback
    }
