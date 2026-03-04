from backend.intelligence.mastery_engine import load_student_mastery

def compute_tutor_difficulty(student_id: str, topic: str) -> str:
    """ Returns the adaptive difficulty string based on historical mastery. """
    profile = load_student_mastery(student_id)
    mastery = profile["topic_mastery"].get(topic.lower().strip(), {}).get("mastery", 0.0)
    
    if mastery >= 0.7:
        return "advanced"
    elif mastery >= 0.4:
        return "intermediate"
    else:
        return "basic"
