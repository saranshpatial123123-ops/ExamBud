import os
import json
from datetime import datetime
from backend.config import settings

def get_mastery_filepath(student_id: str) -> str:
    """Returns the absolute path to a student's mastery JSON file."""
    mastery_dir = os.path.join(settings.BASE_DIR, "data", "student_mastery")
    os.makedirs(mastery_dir, exist_ok=True)
    safe_id = "".join(c for c in student_id if c.isalnum() or c in ('_', '-', '.'))
    return os.path.join(mastery_dir, f"{safe_id}.json")

def load_student_mastery(student_id: str) -> dict:
    """Loads the entire mastery profile for a student, returning an empty skeleton if not found."""
    filepath = get_mastery_filepath(student_id)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"student_id": student_id, "topic_mastery": {}}

def save_student_mastery(student_id: str, data: dict):
    """Saves the mastery profile for a student."""
    filepath = get_mastery_filepath(student_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_topic_mastery(student_id: str, topic: str, accuracy: float, time_taken: int, attempts: int) -> dict:
    """
    Updates the mastery score for a specific topic based on performance signals.
    new_mastery = (0.5 * previous_mastery) + (0.3 * accuracy) + (0.2 * completion_signal)
    """
    profile = load_student_mastery(student_id)
    topic_key = topic.lower().strip()
    
    topic_data = profile["topic_mastery"].get(topic_key, {
        "mastery": 0.0,
        "attempts": 0,
        "review_count": 0,
        "last_reviewed": None,
        "next_review_date": None,
        "avg_accuracy": 0.0
    })
    
    prev_mastery = topic_data["mastery"]
    prev_attempts = topic_data["attempts"]
    prev_avg = topic_data["avg_accuracy"]
    prev_review_count = topic_data.get("review_count", 0)
    
    # Calculate new average accuracy
    total_attempts = prev_attempts + attempts
    new_avg_accuracy = ((prev_avg * prev_attempts) + (accuracy * attempts)) / total_attempts if total_attempts > 0 else accuracy
    
    # Heuristic completion signal based on time_taken / reasonable limits (simplified)
    # E.g. penalize slightly if taking extremely long, reward if efficient
    # Assumes standardized typical time per question, here we just proxy it softly to 1.0 for now
    completion_signal = 1.0 
    
    new_mastery = (0.5 * prev_mastery) + (0.3 * accuracy) + (0.2 * completion_signal)
    
    # Clamp between 0.0 and 1.0
    new_mastery = max(0.0, min(1.0, new_mastery))
    
    topic_data["mastery"] = round(new_mastery, 4)
    topic_data["attempts"] = total_attempts
    topic_data["review_count"] = prev_review_count + 1
    
    today = datetime.now()
    topic_data["last_reviewed"] = today.strftime("%Y-%m-%d")
    
    # Calculate simple next_review_date
    if new_mastery < 0.40:
        days_to_add = 1
    elif new_mastery < 0.60:
        days_to_add = 2
    elif new_mastery < 0.75:
        days_to_add = 4
    elif new_mastery < 0.85:
        days_to_add = 7
    else:
        days_to_add = 14
        
    next_review = today + __import__("datetime").timedelta(days=days_to_add)
    topic_data["next_review_date"] = next_review.strftime("%Y-%m-%d")
    
    topic_data["avg_accuracy"] = round(new_avg_accuracy, 4)
    
    profile["topic_mastery"][topic_key] = topic_data
    
    save_student_mastery(student_id, profile)
    
    return topic_data

def get_mastery_profile(student_id: str, subject: str = None) -> dict:
    """ Retrieves mastery scores. Currently returns all due to decoupled subject mapping. """
    profile = load_student_mastery(student_id)
    return profile
