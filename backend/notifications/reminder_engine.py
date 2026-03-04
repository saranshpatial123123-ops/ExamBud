from typing import List
from backend.timeline.course_timeline import timeline_manager
from backend.learning_state.student_memory import StudentMemory
from backend.knowledge_graph.concept_graph import concept_graph

class ReminderEngine:
    @staticmethod
    def generate_alerts(student_id: str, active_course_ids: List[str]) -> List[str]:
        """
        Sweeps through official timelines, cross-referencing the student's personal mastery cache
        to synthesize immediate actionable alerts.
        """
        alerts = []
        
        # 1. Timeline Deadlines
        for course in active_course_ids:
            upcoming = timeline_manager.get_upcoming_events(course, days_ahead=5)
            for event in upcoming:
                if event["type"] == "quiz":
                    alerts.append(f"Heads up! You have a {event['topic']} Quiz coming up on {event['due']}.")
                elif event["type"] == "assignment":
                    alerts.append(f"Assignment due soon for {event['topic']} ({event['due']}).")
                elif event["type"] == "lab":
                    alerts.append(f"Lab deadline approaching for {event['topic']} ({event['due']}).")
                    
        # 2. Mastery Warnings (Spaced Repetition & Weakness)
        profile = StudentMemory.load_profile(student_id)
        mastery_dict = profile.get("concept_mastery", {})
        
        # Find critically weak concepts
        weak_concepts = [c_id for c_id, score in mastery_dict.items() if score < 0.4]
        
        for weak_id in weak_concepts[:3]: # Only nag about maximum 3 at a time
            concept = concept_graph.get_concept(weak_id)
            if concept:
                alerts.append(f"Revision Recommended: Your mastery in '{weak_id}' is dipping. Try a quick practice set.")
                
        # 3. Missed Goals (Simulated example)
        # Assuming profile stores a daily_goal_streak
        # if profile.get("last_active_date") != today:
        #     alerts.append("You missed yesterday's session! Keep your streak alive today.")
        
        if not alerts:
            alerts.append("You are fully caught up. Great job!")
            
        return alerts
