from datetime import datetime, timedelta
from backend.learning_state.student_memory import StudentMemory

class ConceptMasteryTracker:
    CORRECT_DELTA = 0.05
    INCORRECT_DELTA = -0.02
    DAILY_DECAY = 0.002
    DECAY_GRACE_DAYS = 7
    
    @classmethod
    def update_mastery(cls, student_id: str, concept_id: str, is_correct: bool):
        """
        Updates the mastery score for a specific concept based on a practice/exam attempt.
        """
        profile = StudentMemory.load_profile(student_id)
        
        # Initialize if concept never seen
        current_score = profile["concept_mastery"].get(concept_id, 0.5)
        
        # Apply delta
        delta = cls.CORRECT_DELTA if is_correct else cls.INCORRECT_DELTA
        new_score = current_score + delta
        
        # Clamp between 0.0 and 1.0
        new_score = max(0.0, min(1.0, new_score))
        
        # Update dictionaries
        profile["concept_mastery"][concept_id] = round(new_score, 4)
        profile["last_practiced"][concept_id] = datetime.utcnow().isoformat()
        
        StudentMemory.save_profile(profile)
        return new_score

    @classmethod
    def apply_decay(cls, student_id: str):
        """
        Applies mathematical Spaced Repetition decay to all concepts a student knows.
        If a concept is not practiced for DECAY_GRACE_DAYS, it drops by DAILY_DECAY each day.
        Run this as a nightly task.
        """
        profile = StudentMemory.load_profile(student_id)
        now = datetime.utcnow()
        updated = False
        
        for concept_id, last_date_str in profile.get("last_practiced", {}).items():
            try:
                last_date = datetime.fromisoformat(last_date_str)
                days_since = (now - last_date).days
                
                if days_since > cls.DECAY_GRACE_DAYS:
                    # Calculate how many days of decay to apply past the grace window
                    decay_days = days_since - cls.DECAY_GRACE_DAYS
                    total_decay = decay_days * cls.DAILY_DECAY
                    
                    current_score = profile["concept_mastery"].get(concept_id, 0.5)
                    new_score = current_score - total_decay
                    
                    # Clamp
                    new_score = max(0.0, min(1.0, new_score))
                    
                    if new_score != current_score:
                        profile["concept_mastery"][concept_id] = round(new_score, 4)
                        # We do NOT update last_practiced here. Decay continues until practically verified again.
                        updated = True
            except ValueError:
                continue
                
        if updated:
            StudentMemory.save_profile(profile)
            
    @classmethod
    def get_concept_score(cls, student_id: str, concept_id: str) -> float:
        """Helper to quickly fetch a student's score for a concept."""
        profile = StudentMemory.load_profile(student_id)
        # Default unseen concepts start at 0.5 neutrality
        return profile.get("concept_mastery", {}).get(concept_id, 0.5)
