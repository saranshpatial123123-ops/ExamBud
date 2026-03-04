import os
import glob
from backend.learning_state.concept_mastery_tracker import ConceptMasteryTracker
from backend.notifications.reminder_engine import ReminderEngine
from backend.learning_state.student_memory import CACHE_DIR

def run_nightly_decay():
    """
    Iterates through all localized student memory files and applies the mathematical Daily Decay Spaced Repetition logic.
    """
    files = glob.glob(os.path.join(CACHE_DIR, "*.json"))
    affected_count = 0
    
    for f in files:
        filename = os.path.basename(f)
        student_id = filename.replace(".json", "")
        # Apply strict memory decay internally
        ConceptMasteryTracker.apply_decay(student_id)
        affected_count += 1
        
    print(f"[Nightly Task] Processed spaced repetition mastery decay for {affected_count} student profiles.")

def dispatch_daily_notifications():
    """
    Bulk generates notifications and hypothetically dispatches emails/push notifications.
    """
    files = glob.glob(os.path.join(CACHE_DIR, "*.json"))
    for f in files:
        student_id = os.path.basename(f).replace(".json", "")
        
        # Simulating fetching the student's active courses from a primary database
        active_courses = ["CS301-OS"]  
        
        alerts = ReminderEngine.generate_alerts(student_id, active_courses)
        
        # Hypothetical email/push dispatch here
        # send_push_notification(student_id, alerts)
        print(f"[Notifications] Dispatched {len(alerts)} alerts to student {student_id}")

# These tasks would be wired into Celery Beat or a server Cron entry in production.
