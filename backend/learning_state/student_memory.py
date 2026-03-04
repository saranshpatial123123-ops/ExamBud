import os
import json
from datetime import datetime
from backend.config import settings

# A centralized file-based cache for student memory.
# Schema:
# {
#    "student_id": "1234",
#    "concept_mastery": {
#        "mutual_exclusion": 0.82,
#        "circular_wait": 0.28
#    },
#    "last_practiced": {
#        "mutual_exclusion": "2026-03-01T10:00:00",
#        "circular_wait": "2026-02-28T14:30:00"
#    }
# }

CACHE_DIR = os.path.join(settings.BASE_DIR, "data", "memory_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class StudentMemory:
    @staticmethod
    def _get_file_path(student_id: str) -> str:
        return os.path.join(CACHE_DIR, f"{student_id}.json")

    @classmethod
    def load_profile(cls, student_id: str) -> dict:
        """Loads a student's entire learning profile from the JSON cache."""
        path = cls._get_file_path(student_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
                
        # Return default blank profile if missing or corrupted
        return {
            "student_id": student_id,
            "concept_mastery": {},
            "last_practiced": {}
        }

    @classmethod
    def save_profile(cls, profile: dict):
        """Persists the updated student profile back to the JSON cache."""
        student_id = profile.get("student_id")
        if not student_id:
            raise ValueError("Cannot save profile without student_id")
            
        path = cls._get_file_path(student_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=4)
