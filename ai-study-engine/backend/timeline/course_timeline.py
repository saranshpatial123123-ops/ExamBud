from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TimelineEvent(BaseModel):
    week_number: int
    topic: str
    assignment_deadline: Optional[str] = None # ISO format date
    quiz_date: Optional[str] = None # ISO format date
    lab_deadline: Optional[str] = None # ISO format date
    
class CourseTimeline(BaseModel):
    course_id: str
    institute: str
    branch: str
    events: List[TimelineEvent] = []

class TimelineManager:
    """
    Simulates a database table managing official course timelines.
    """
    def __init__(self):
        self._timelines = {}

    def save_timeline(self, timeline: CourseTimeline):
        self._timelines[timeline.course_id] = timeline
        
    def get_timeline(self, course_id: str) -> Optional[CourseTimeline]:
        return self._timelines.get(course_id)
        
    def get_upcoming_events(self, course_id: str, days_ahead: int = 7) -> List[dict]:
        """
        Retrieves all assignments, quizzes, and labs due within the next N days.
        """
        timeline = self.get_timeline(course_id)
        if not timeline:
            return []
            
        upcoming = []
        now = datetime.utcnow()
        threshold = now.timestamp() + (days_ahead * 86400)
        
        for event in timeline.events:
            # Check assignment
            if event.assignment_deadline:
                dt = datetime.fromisoformat(event.assignment_deadline)
                if now.timestamp() <= dt.timestamp() <= threshold:
                    upcoming.append({"type": "assignment", "topic": event.topic, "due": event.assignment_deadline})
            
            # Check quiz
            if event.quiz_date:
                dt = datetime.fromisoformat(event.quiz_date)
                if now.timestamp() <= dt.timestamp() <= threshold:
                    upcoming.append({"type": "quiz", "topic": event.topic, "due": event.quiz_date})
            
            # Check lab
            if event.lab_deadline:
                dt = datetime.fromisoformat(event.lab_deadline)
                if now.timestamp() <= dt.timestamp() <= threshold:
                    upcoming.append({"type": "lab", "topic": event.topic, "due": event.lab_deadline})
                    
        return upcoming

timeline_manager = TimelineManager()

# Seed an example course
timeline_manager.save_timeline(CourseTimeline(
    course_id="CS301-OS",
    institute="default",
    branch="cs",
    events=[
        TimelineEvent(week_number=1, topic="Processes", assignment_deadline="2026-09-07T23:59:00"),
        TimelineEvent(week_number=2, topic="Threads", lab_deadline="2026-09-14T17:00:00"),
        TimelineEvent(week_number=3, topic="Scheduling", quiz_date="2026-09-20T10:00:00"),
        TimelineEvent(week_number=4, topic="Deadlocks", assignment_deadline="2026-09-27T23:59:00"),
    ]
))
