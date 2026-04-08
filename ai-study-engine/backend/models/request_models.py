from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    question: str
    institute: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[str] = None
    subject: Optional[str] = None

class CourseScopeRequest(BaseModel):
    institute: str
    branch: str
    semester: str
    subject: str

class StudyPlanRequest(BaseModel):
    institute: str
    branch: str
    semester: str
    subject: str
    exam_date: str
    daily_study_hours: float
    preferred_difficulty: str = "balanced"
    weak_topics: list[str] = []
    strong_topics: list[str] = []
    events: list[dict] = []
    course_credits: float = 4.0
    course_difficulty: str = "medium"
    student_id: Optional[str] = None

class MarkProgressRequest(BaseModel):
    plan_id: str
    date: str
    completed_tasks: list[str]

class UpdateMasteryRequest(BaseModel):
    student_id: str
    topic: str
    accuracy: float
    time_taken: int
    attempts: int

class AnalyzeCourseRequest(BaseModel):
    institute: str
    branch: str
    semester: str
    subject: str

class TutorSessionRequest(BaseModel):
    student_id: str
    institute: str
    branch: str
    semester: str
    subject: str
    topic: str

class TutorAnswerRequest(BaseModel):
    student_id: str
    session_id: str
    topic: str
    answers: list[dict]

class PracticeSetRequest(BaseModel):
    student_id: str
    institute: str
    branch: str
    semester: str
    subject: str
    topic: str
    count: int = 5

class ExamGenerationRequest(BaseModel):
    student_id: str
    institute: str
    branch: str
    semester: str
    subject: str
    exam_duration: int = 45
    question_count: int = 30

class ExamEvaluationRequest(BaseModel):
    student_id: str
    subject: str
    student_answers: list[dict]
    answer_key: list[dict]
