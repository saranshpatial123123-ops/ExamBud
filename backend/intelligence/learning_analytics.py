from backend.intelligence.mastery_engine import load_student_mastery

def get_learning_analytics(student_id: str) -> dict:
    """
    Computes aggregated analytics mapping a student's strengths and weaknesses.
    """
    profile = load_student_mastery(student_id)
    topic_data = profile.get("topic_mastery", {})
    
    strong_topics = []
    weak_topics = []
    total_mastery = 0.0
    active_topics = 0
    total_attempts = 0
    
    for topic, stats in topic_data.items():
        mastery = stats.get("mastery", 0.0)
        attempts = stats.get("attempts", 0)
        
        if attempts > 0:
            active_topics += 1
            total_mastery += mastery
            total_attempts += attempts
            
        if mastery >= 0.7:
            strong_topics.append({"topic": topic.title(), "mastery": mastery})
        elif mastery < 0.4:
            weak_topics.append({"topic": topic.title(), "mastery": mastery})
            
    # Sort for best presentation
    strong_topics.sort(key=lambda x: x["mastery"], reverse=True)
    weak_topics.sort(key=lambda x: x["mastery"])
    
    return {
        "student_id": student_id,
        "overall_readiness": total_mastery / active_topics if active_topics > 0 else 0.0,
        "total_active_topics": active_topics,
        "total_practice_attempts": total_attempts,
        "strong_topics": [s["topic"] for s in strong_topics],
        "weak_topics": [w["topic"] for w in weak_topics]
    }
