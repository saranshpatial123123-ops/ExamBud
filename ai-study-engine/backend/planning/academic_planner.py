import os
import json
import uuid
import math
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.config import settings
from backend.planning.study_planner import load_topic_graph
from backend.utils.logging_utils import get_logger

logger = get_logger("AcademicPlanner")

class TaskType:
    TOPIC = "topic"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    HOMEWORK = "homework"
    LAB = "lab"
    PROJECT = "project"
    REVISION = "revision"

class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"
    CARRIED_OVER = "carried_over"

class UnifiedTask(BaseModel):
    task_id: str
    type: str
    title: str
    estimated_hours: float
    priority_score: float = 0.0
    deadline: Optional[str] = None
    status: str = TaskStatus.PENDING
    remaining_hours: float = 0.0
    days_scheduled: int = 0  # To enforce assignment atomicity (<= 3 days)
    prerequisites: List[str] = []

def calculate_priority_score(
    item_type: str,
    base_weight: float,
    exam_weightage: float = 0.5,
    topic_depth: float = 0.5,
    topic_difficulty: float = 0.5,
    recurrence_rate: float = 0.5,
    student_weakness: float = 0.5,
    course_credits: float = 0.5,
    prerequisite_importance: float = 0.5,
    mastery_score: float = 0.0,
    days_until_due: float = None
) -> float:
    """
    Computes priority based on institutional and student signals.
    Normalize values between 0.0 and 1.0.
    """
    # Base formula
    score = (
        0.30 * exam_weightage +
        0.20 * topic_depth +
        0.15 * topic_difficulty +
        0.15 * recurrence_rate +
        0.10 * student_weakness +
        0.05 * course_credits +
        0.05 * prerequisite_importance
    )
    
    # Mastery adjustment
    if item_type == TaskType.TOPIC:
        score += (1.0 - mastery_score) * 0.25
    
    # Event-specific urgency modifier
    if item_type != TaskType.TOPIC and days_until_due is not None:
        if days_until_due <= 0:
            urgency = 1.0  # Immediate
        else:
            urgency = min(1.0, 1.0 / days_until_due)
        score += 0.20 * urgency
        
    return min(1.0, score * base_weight)

def extract_tasks_from_graph(
    institute: str, branch: str, semester: str, subject: str,
    weak_topics: list, strong_topics: list, student_id: str = None
) -> dict:
    """Extracts topic tasks from the JSON syllabus. Returns dict with tasks and forced prereq reviews."""
    graph = load_topic_graph(institute, branch, semester, subject)
    topics = graph.get("topics", [])
    
    # Load mastery if available
    mastery_data = {}
    if student_id:
        try:
            from backend.intelligence.mastery_engine import load_student_mastery
            profile = load_student_mastery(student_id)
            mastery_data = profile.get("topic_mastery", {})
        except Exception:
            pass # Ignore if module missing or error loading profile
            
    # Load concept graph for prerequisites
    concept_graph = {}
    try:
        from backend.knowledge_graph.concept_graph import load_concept_graph
        cg = load_concept_graph(institute, branch, semester, subject)
        for c in cg.get("concepts", []):
            concept_graph[c.get("concept", "").lower().strip()] = c.get("prerequisites", [])
    except Exception:
        pass
            
    tasks = []
    forced_prereq_reviews = []
    
    # Simple heuristic normalizations for missing institutional data
    for idx, t in enumerate(topics):
        topic_name = t.get("name", "Unknown Topic")
        subtopics = t.get("subtopics", [])
        
        # Estimate depth based on subtopics
        topic_depth = min(1.0, len(subtopics) / 10.0) 
        
        weight_modifier = 1.0
        student_weakness = 0.5
        topic_lower = topic_name.lower().strip()
        prereqs = concept_graph.get(topic_lower, [])
        prereqs = [p.lower().strip() for p in prereqs]
        
        if any(wt in topic_lower for wt in weak_topics):
            weight_modifier = 1.5
            student_weakness = 1.0
        elif any(st in topic_lower for st in strong_topics):
            weight_modifier = 0.5
            student_weakness = 0.0
            
        # Parse mastery for this specific topic
        topic_mastery = 0.0
        if topic_lower in mastery_data:
            topic_mastery = mastery_data[topic_lower].get("mastery", 0.0)
            
            # Review trigger logic override for priority multiplier
            if topic_mastery < 0.4:
                weight_modifier = max(weight_modifier, 1.5)  # Auto-flag as weak
                # Trigger prerequisite reviews
                for p in prereqs:
                    forced_prereq_reviews.append(p)
                    
            elif topic_mastery > 0.85:
                weight_modifier = min(weight_modifier, 0.5)  # Auto-reduce repetition
            
        priority = calculate_priority_score(
            item_type=TaskType.TOPIC,
            base_weight=weight_modifier,
            topic_depth=topic_depth,
            student_weakness=student_weakness,
            mastery_score=topic_mastery
        )
        
        # Est 1 hour per subtopic + 1 hour for the main topic
        est_hours = max(0.5, (len(subtopics) * 1.0) + 1.0)
        
        task_id = f"topic_{idx}_{hash(topic_name) % 10000}"
        tasks.append(UnifiedTask(
            task_id=task_id,
            type=TaskType.TOPIC,
            title=topic_name,
            estimated_hours=est_hours,
            remaining_hours=est_hours,
            priority_score=priority,
            prerequisites=prereqs
        ))
    return {"tasks": tasks, "forced_prereq_reviews": list(set(forced_prereq_reviews))}

def process_events_to_tasks(events: List[dict], today: datetime.date) -> List[UnifiedTask]:
    """Converts user-provided events into Unified Tasks."""
    tasks = []
    for idx, ev in enumerate(events):
        due_date_str = ev.get("due_date", None)
        days_until_due = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            days_until_due = max(0, (due_date - today).days)
            
        priority = calculate_priority_score(
            item_type=ev.get("type", TaskType.ASSIGNMENT),
            base_weight=1.0,
            days_until_due=days_until_due
        )
        
        tasks.append(UnifiedTask(
            task_id=f"event_{idx}_{uuid.uuid4().hex[:6]}",
            type=ev.get("type", TaskType.ASSIGNMENT),
            title=ev.get("title", "Unnamed Event"),
            estimated_hours=float(ev.get("estimated_hours", 2.0)),
            remaining_hours=float(ev.get("estimated_hours", 2.0)),
            deadline=due_date_str,
            priority_score=priority
        ))
    return tasks

def generate_academic_schedule(
    institute: str, branch: str, semester: str, subject: str,
    exam_date: str, daily_study_hours: float, preferred_difficulty: str,
    weak_topics: list, strong_topics: list, events: list = None,
    carry_over_tasks: list = None, student_id: str = None
) -> dict:
    """
    Main scheduling engine.
    Follows constraints: Max daily load, Carry-over > Deadlines > Topics, min chunking, revision buffers.
    """
    today = datetime.now().date()
    exam_d = datetime.strptime(exam_date, "%Y-%m-%d").date()
    days_available = (exam_d - today).days
    
    if days_available <= 0:
        raise ValueError("Exam date must be in the future.")
        
    events = events or []
    carry_over_tasks = carry_over_tasks or []
    
    logger.info(f"Generating schedule for {institute}/{branch} '{subject}' by {exam_date}. {len(events)} events provided.")
    
    # Load all tasks
    extraction = extract_tasks_from_graph(institute, branch, semester, subject, weak_topics, strong_topics, student_id)
    topic_tasks = extraction["tasks"]
    forced_prereq_reviews = extraction["forced_prereq_reviews"]
    
    event_tasks = process_events_to_tasks(events, today)
    
    # Load Spaced Repetition Review Tasks
    review_tasks = []
    if student_id:
        try:
            from backend.intelligence.spaced_repetition import generate_review_tasks
            review_tasks = generate_review_tasks(student_id, subject)
        except Exception:
            pass
            
    # Inject forced prerequisite reviews into review_tasks if not already present
    existing_review_titles = {t.title.lower() for t in review_tasks}
    for prereq in forced_prereq_reviews:
        expected_title = f"review: {prereq}".lower()
        if expected_title not in existing_review_titles:
            review_tasks.append(UnifiedTask(
                task_id=f"forced_review_{prereq.replace(' ', '_')}",
                type=TaskType.REVISION,
                title=f"Review: {prereq.title()} (Prerequisite)",
                estimated_hours=0.5,
                remaining_hours=0.5,
                priority_score=1.0 # Max priority to unblock dependent topic
            ))
    
    # Restore carry-over state if this is a reschedule
    carry_over_map = {t["task_id"]: t for t in carry_over_tasks}
    
    all_pending_tasks = []
    for t in topic_tasks + event_tasks + review_tasks:
        if t.task_id in carry_over_map:
            # Overwrite with carry-over state
            c_task = carry_over_map[t.task_id]
            t.remaining_hours = float(c_task.get("remaining_hours", t.remaining_hours))
            t.status = TaskStatus.CARRIED_OVER
        all_pending_tasks.append(t)
        
    # Add explicit carry over tasks that might not be in the base topics/events anymore
    existing_ids = {t.task_id for t in all_pending_tasks}
    for c_task in carry_over_tasks:
        if c_task.get("task_id") not in existing_ids and c_task.get("status") != TaskStatus.COMPLETED:
            all_pending_tasks.append(UnifiedTask(**c_task))

    # Calculate total workload
    total_required_hours = sum(t.remaining_hours for t in all_pending_tasks)
    total_available_hours = days_available * daily_study_hours
    
    # 1. Carry-over safeguard check
    carry_over_hours = sum(t.get('remaining_hours', 0) for t in carry_over_tasks)
    max_carryover_allowed = daily_study_hours * 3.0
    
    # Emergency Compression Logic
    emergency_message = None
    if total_required_hours > total_available_hours or carry_over_hours > max_carryover_allowed:
        if carry_over_hours > max_carryover_allowed:
            emergency_message = "You have accumulated too many missed tasks. The system has entered priority recovery mode to ensure you pass."
            logger.warning("Emergency State Triggered: Excessive carry-over block logic activated.")
        else:
            emergency_message = "Your remaining time is insufficient to cover the full syllabus. The system has prioritized high-weight topics."
            logger.warning("Emergency State Triggered: Insufficient study hours available for target content constraint.")
            
        # Keep assignments, drop lowest priority topics until we fit
        all_pending_tasks.sort(key=lambda x: (x.type != TaskType.TOPIC, x.priority_score), reverse=True)
        
        retained = []
        csum = 0
        for t in all_pending_tasks:
            if csum + t.remaining_hours <= total_available_hours or t.type != TaskType.TOPIC:
                retained.append(t)
                csum += t.remaining_hours
        all_pending_tasks = retained

    # Scheduling Engine
    schedule = []
    max_daily_load = daily_study_hours * 1.3
    min_chunk = 0.5  # Prevent splitting into silly chunks like 0.08 hours
    
    # To protect revision buffer (15% of days)
    revision_days = max(1, int(days_available * 0.15))
    planning_days = days_available - revision_days
    if planning_days <= 0: planning_days = days_available
    
    for day_offset in range(planning_days):
        current_date_obj = today + timedelta(days=day_offset)
        current_date_str = current_date_obj.strftime("%Y-%m-%d")
        
        daily_hours_allocated = 0.0
        daily_tasks = []
        
        # Sort queue for today: Carry Over -> Urgent Deadlines -> Review -> Normal Topics -> Revision Output
        def sort_key(t: UnifiedTask):
            # Distance to deadline
            days_to_dl = 999
            if t.deadline:
                dl_date = datetime.strptime(t.deadline, "%Y-%m-%d").date()
                days_to_dl = (dl_date - current_date_obj).days
            
            is_urgent_deadline = 1 if days_to_dl <= 2 else 0
            is_carry_over = 1 if t.status == TaskStatus.CARRIED_OVER else 0
            is_review = 1 if t.type == TaskType.REVISION and "Review:" in t.title else 0
            
            # 1. Carry over overrides
            # 2. Urgent deadlines
            # 3. Spaced Repetition Review (Before new topics)
            # 4. Overall Priority Score
            return (is_carry_over, is_urgent_deadline, is_review, t.priority_score)

        all_pending_tasks.sort(key=sort_key, reverse=True)
        
        daily_review_allocated = 0.0
        max_daily_review = daily_study_hours * 0.40 # Max 40% of time on reviews
        
        completed_or_scheduled_concept_titles = {t["title"].lower().strip() for d in schedule for t in d.get("tasks", [])}
        for dt in daily_tasks:
            completed_or_scheduled_concept_titles.add(dt["title"].lower().strip())
            
        deferred_tasks = []
        
        for task in list(all_pending_tasks):
            if task.remaining_hours <= 0:
                all_pending_tasks.remove(task)
                continue
                
            if daily_hours_allocated >= max_daily_load:
                break
                
            # PREREQUISITE CHECK:
            # If this is a new topic, ensure all its prerequisites have been scheduled in previous days or earlier today.
            if task.type == TaskType.TOPIC and task.prerequisites:
                prereqs_met = True
                for p in task.prerequisites:
                    # Loosely check if prereq title is in completed set. 
                    # If it's not yet scheduled, we must defer this task to a future day.
                    if p.lower().strip() not in completed_or_scheduled_concept_titles:
                        prereqs_met = False
                        break
                if not prereqs_met:
                    deferred_tasks.append(task)
                    continue
                
            # If it's a review task, enforce the 40% cap
            is_review_task = task.type == TaskType.REVISION and "Review:" in task.title
            available_review_slot = max_daily_review - daily_review_allocated
            
            if is_review_task and available_review_slot <= 0:
                continue # Push remaining review tasks to tomorrow
                
            # How much to allocate?
            available_slot = max_daily_load - daily_hours_allocated
            alloc = min(task.remaining_hours, available_slot)
            
            if is_review_task:
                alloc = min(alloc, available_review_slot)
            
            # Safeguard 1: Task Atomicity (min chunk 0.5hr unless task itself is small)
            if alloc < min_chunk and task.remaining_hours > alloc:
                if daily_hours_allocated > 0:
                    continue # Try again tomorrow when there's more space
                else: # Forced to do it if it's the only thing
                    alloc = task.remaining_hours # Let it overflow slightly if needed

            # Safeguard 2: Assignment splitting (max 3 days)
            if task.type != TaskType.TOPIC and task.days_scheduled >= 2 and task.remaining_hours > alloc:
                # Force finish it today to satisfy atomicity <= 3 days
                alloc = task.remaining_hours

            alloc = round(alloc, 2)
            task.remaining_hours -= alloc
            task.days_scheduled += 1
            daily_hours_allocated += alloc
            
            if is_review_task:
                daily_review_allocated += alloc
            
            daily_tasks.append({
                "task_id": task.task_id,
                "type": task.type,
                "title": task.title,
                "allocated_hours": alloc,
                "deadline": task.deadline
            })
            
            # Once scheduled, it counts as met for prerequisites later today
            completed_or_scheduled_concept_titles.add(task.title.lower().strip())
            
            if task.remaining_hours <= 0:
                all_pending_tasks.remove(task)
                
        schedule.append({
            "date": current_date_str,
            "tasks": daily_tasks,
            "total_allocated": round(daily_hours_allocated, 2)
        })

    # Remaining Days = Revision Buffer / Emergency Dump
    for day_offset in range(planning_days, days_available):
        current_date_obj = today + timedelta(days=day_offset)
        schedule.append({
            "date": current_date_obj.strftime("%Y-%m-%d"),
            "tasks": [{"type": "revision", "title": "Revision Buffer", "allocated_hours": daily_study_hours}],
            "total_allocated": daily_study_hours
        })

    plan_id = str(uuid.uuid4())
    
    result = {
        "status": "success",
        "plan_version": 1,
        "plan_id": plan_id,
        "course_scope": {
             "institute": institute,
             "branch": branch,
             "semester": semester,
             "subject": subject
        },
        "days_scheduled": len(schedule),
        "total_study_hours_budgeted": round(total_available_hours, 1),
        "emergency_mode_active": emergency_message is not None,
        "messages": [emergency_message] if emergency_message else [],
        "schedule": schedule
    }
    
    # Storage
    plans_dir = os.path.join(settings.BASE_DIR, "data", "study_plans")
    os.makedirs(plans_dir, exist_ok=True)
    filepath = os.path.join(plans_dir, f"{plan_id}.json")
    
    with open(filepath, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    logger.info(f"Generated new plan '{plan_id}' with {result['days_scheduled']} operational blocks for {result['total_study_hours_budgeted']} hours context.")
    return result

def mark_day_progress(plan_id: str, date_str: str, completed_task_ids: list) -> dict:
    """
    1. Loads the plan.
    2. Identifies tasks meant for `date_str` that were missed.
    3. Triggers rescheduling to shift missed tasks into Carry Over.
    """
    plans_dir = os.path.join(settings.BASE_DIR, "data", "study_plans")
    filepath = os.path.join(plans_dir, f"{plan_id}.json")
    
    logger.info(f"Marking daily progress for {plan_id} on {date_str}. {len(completed_task_ids)} objectives reported complete.")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError("Study plan not found.")
        
    with open(filepath, "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    # Extract missed tasks to carry over
    carry_over = []
    messages = []
    
    for day in plan.get("schedule", []):
        if day["date"] == date_str:
            for task in day.get("tasks", []):
                # Revision blocks aren't tracked
                if task.get("type") == "revision": continue
                    
                if task["task_id"] not in completed_task_ids:
                    carry_over.append({
                        "task_id": task["task_id"],
                        "type": task.get("type"),
                        "title": task.get("title"),
                        "remaining_hours": task.get("allocated_hours"),
                        "status": TaskStatus.CARRIED_OVER,
                        "deadline": task.get("deadline"),
                        "priority_score": 1.0 # High priority via reschedule logic
                    })
                else:
                    # Update status and timestamp for analytics
                    task["status"] = TaskStatus.COMPLETED
                    task["completed_at"] = datetime.now().isoformat()
                    
    # Save the updated progress back to the plan JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
                    
    if carry_over:
        messages.append("You missed yesterday's tasks. They have been rescheduled for today.")
    else:
        messages.append("Great job completing your daily goals!")
        
    # To correctly recalculate automatically, we need original exam_date and hours.
    # We now instruct clients to trigger `/generate_study_plan` again passing these carry_over items
    # to receive the formally rescheduled plan.
    
    return {
        "status": "success",
        "messages": messages,
        "carried_over_tasks": len(carry_over),
        "carry_over_items": carry_over,
        "instruction": "Progress saved. Resubmit to /generate_study_plan with `carry_over_tasks` to finalize new schedule."
    }
