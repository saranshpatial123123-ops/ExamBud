from datetime import datetime
from typing import List
from backend.intelligence.mastery_engine import load_student_mastery
from backend.planning.academic_planner import UnifiedTask, TaskType

def generate_review_tasks(student_id: str, subject: str = None) -> List[UnifiedTask]:
    """
    Scans a student's mastery profile and checks the `next_review_date`.
    Returns a list of UnifiedTask objects for topics that need reviewing today or earlier.
    """
    profile = load_student_mastery(student_id)
    topic_mastery = profile.get("topic_mastery", {})
    
    if not topic_mastery:
        return []
        
    tasks = []
    today = datetime.now().date()
    
    for topic_name, data in topic_mastery.items():
        # Only process topics with a set review date
        review_date_str = data.get("next_review_date")
        if not review_date_str:
            continue
            
        review_date = datetime.strptime(review_date_str, "%Y-%m-%d").date()
        
        # If it's due today or overdue
        if review_date <= today:
            
            mastery_score = data.get("mastery", 0.0)
            
            # Priority formula: high if heavily overdue or very low mastery
            days_overdue = (today - review_date).days
            overdue_multiplier = min(1.0, days_overdue * 0.1)  # Max +0.1 for being 1+ days late
            
            # Base logic: weak topics are extremely high priority for review
            priority = (1.0 - mastery_score) * 0.8 + 0.2 + overdue_multiplier
            priority = min(1.0, priority)
            
            # Review tasks take 0.5 hours by default
            estimated_hours = 0.5
            
            tasks.append(UnifiedTask(
                task_id=f"review_{topic_name.replace(' ', '_')}",
                type=TaskType.REVISION, # Reusing revision as the type, but with specific titles
                title=f"Review: {topic_name.title()}",
                estimated_hours=estimated_hours,
                remaining_hours=estimated_hours,
                priority_score=priority,
                deadline=None
            ))
            
    return tasks
