import os
import json
import math
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from backend.config import settings

def load_topic_graph(institute: str, branch: str, semester: str, subject: str) -> dict:
    """Loads the pre-generated JSON topic graph for the given course scope."""
    graphs_dir = os.path.join(settings.BASE_DIR, "data", "topic_graphs")
    filename = f"{institute}_{branch}_{semester}_{subject}.json"
    filename = "".join(c for c in filename if c.isalnum() or c in ('_', '.', '-'))
    
    filepath = os.path.join(graphs_dir, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError("Topic graph not found. Please analyze the course materials first.")
        
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def estimate_topic_weight(topic: dict, subtopics: list, weak_topics: list, strong_topics: list) -> float:
    """
    Estimates the weight (relative time requirement) of a topic.
    Base weight correlates to the number of subtopics.
    Prioritizes topics that are marked 'weak' and de-prioritizes 'strong'.
    """
    topic_name = topic.get("name", "").lower()
    
    # Base weight depends on how many subtopics there are (minimum 1.0)
    base_weight = max(1.0, len(subtopics) * 0.5)
    
    # Multipliers
    if any(wt in topic_name for wt in weak_topics):
        base_weight *= 2.0
    if any(st in topic_name for st in strong_topics):
        base_weight *= 0.5
        
    return base_weight

def allocate_study_hours(topics: list, total_hours: float, weak_topics: list, strong_topics: list) -> list:
    """
    Distributes the total available study hours proportionally across topics 
    based on their estimated weights.
    """
    topic_requirements = []
    total_weight = 0.0
    
    # Calculate weights
    for t in topics:
        topic_name = t.get("name", "Unknown Topic")
        subtopics = t.get("subtopics", [])
        
        weight = estimate_topic_weight(t, subtopics, weak_topics, strong_topics)
        total_weight += weight
        
        # Flatten topic with its subtopics for scheduling
        items_to_cover = [topic_name] + subtopics
        topic_requirements.append({
            "items": items_to_cover,
            "weight": weight
        })

    # Allocate hours proportionally
    allocated_topics = []
    for req in topic_requirements:
        # Avoid division by zero
        proportion = req["weight"] / total_weight if total_weight > 0 else 1.0/len(topics)
        hours = total_hours * proportion
        
        allocated_topics.append({
            "items": req["items"],
            "allocated_hours": hours
        })
        
    return allocated_topics

def generate_daily_schedule(allocated_topics: list, daily_study_hours: float) -> list:
    """
    Bins the allocated items into a day-by-day JSON schedule.
    """
    schedule = []
    current_day = 1
    current_day_hours_remaining = daily_study_hours
    current_day_topics = []
    
    for t in allocated_topics:
        items = t["items"]
        hours_needed = t["allocated_hours"]
        
        # Determine items per hour chunk to distribute them across days if needed
        hours_per_item = hours_needed / len(items) if items else 0
        
        for item in items:
            if current_day_hours_remaining < hours_per_item and current_day_hours_remaining < (daily_study_hours * 0.2):
                # Day is mostly full, move to next day
                schedule.append({
                    "day": current_day,
                    "topics": current_day_topics,
                    "estimated_hours": round(daily_study_hours - current_day_hours_remaining, 1)
                })
                current_day += 1
                current_day_hours_remaining = daily_study_hours
                current_day_topics = []
                
            current_day_topics.append(item)
            current_day_hours_remaining -= hours_per_item
            
    # Add final day if not exactly zeroed out
    if current_day_topics:
        schedule.append({
            "day": current_day,
            "topics": current_day_topics,
            "estimated_hours": round(daily_study_hours - current_day_hours_remaining, 1)
        })

    return schedule

def generate_study_plan(
    institute: str, branch: str, semester: str, subject: str,
    exam_date: str, daily_study_hours: float, preferred_difficulty: str,
    weak_topics: list, strong_topics: list
) -> dict:
    """
    Core orchestrator:
    1. Reads Topic Graph
    2. Computes available days -> total hours
    3. Allocates proportionally
    4. Bins into days
    """
    
    # 1. Load Topic Graph
    graph = load_topic_graph(institute, branch, semester, subject)
    topics = graph.get("topics", [])
    if not topics:
        raise ValueError("Topic graph is empty. Cannot generate a plan.")

    # 2. Compute Days & Time
    try:
        exam = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_available = (exam - today).days
        if days_available <= 0:
            raise ValueError("Exam date must be in the future.")
    except ValueError as e:
        if "Exam date" in str(e):
            raise e
        raise ValueError("exam_date must be formatted as YYYY-MM-DD")
        
    total_hours = days_available * daily_study_hours
    
    # Clean topic lists
    weak_topics = [w.lower().strip() for w in weak_topics]
    strong_topics = [s.lower().strip() for s in strong_topics]

    # 3. Allocation mapping
    allocated = allocate_study_hours(topics, total_hours, weak_topics, strong_topics)
    
    # 4. Bin to Schedule
    schedule = generate_daily_schedule(allocated, daily_study_hours)
    
    result = {
        "status": "success",
        "course_scope": {
            "institute": institute,
            "branch": branch,
            "semester": semester,
            "subject": subject
        },
        "days_allocated": len(schedule),
        "total_study_hours_budgeted": round(total_hours, 1),
        "study_plan": schedule
    }
    
    # Persist the plan (optional)
    plans_dir = os.path.join(settings.BASE_DIR, "data", "study_plans")
    os.makedirs(plans_dir, exist_ok=True)
    
    # Safe filename matching scope + timestamp
    scope_str = f"{institute}_{branch}_{semester}_{subject}"
    safe_scope = "".join(c for c in scope_str if c.isalnum() or c in ('_', '.', '-'))
    filename = f"{safe_scope}_plan.json"
    
    filepath = os.path.join(plans_dir, filename)
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    return result
