from fastapi import APIRouter, HTTPException
from typing import Optional
from backend.models.request_models import (
    CourseScopeRequest, StudyPlanRequest, MarkProgressRequest, UpdateMasteryRequest,
    AnalyzeCourseRequest, TutorSessionRequest, TutorAnswerRequest, PracticeSetRequest,
    ExamGenerationRequest, ExamEvaluationRequest
)
from backend.database.core import get_unique_metadata
from backend.knowledge_graph.topic_graph import generate_topic_graph
from backend.planning.academic_planner import generate_academic_schedule, mark_day_progress
from backend.intelligence.mastery_engine import update_topic_mastery, get_mastery_profile
from backend.intelligence.spaced_repetition import generate_review_tasks
from backend.knowledge_graph.concept_graph import generate_concept_graph
from backend.intelligence.adaptive_tutor import generate_tutor_session, evaluate_tutor_answers
from backend.intelligence.learning_analytics import get_learning_analytics
from backend.intelligence.practice_engine import generate_practice_set
from backend.intelligence.exam_simulator import generate_exam, evaluate_exam
from backend.analytics.institute_analytics import InstituteAnalytics
from backend.notifications.reminder_engine import ReminderEngine
from backend.timeline.course_timeline import timeline_manager, CourseTimeline

router = APIRouter(tags=["Study, Intelligence & Planning"])

@router.get("/institutes")
def list_institutes():
    return get_unique_metadata("institute")

@router.get("/branches/{institute}")
def list_branches(institute: str):
    return get_unique_metadata("branch", {"institute": institute.lower()})

@router.get("/semesters/{institute}/{branch}")
def list_semesters(institute: str, branch: str):
    return get_unique_metadata("semester", {"institute": institute.lower(), "branch": branch.lower()})

@router.get("/subjects/{institute}/{branch}/{semester}")
def list_subjects(institute: str, branch: str, semester: str):
    return get_unique_metadata("subject", {"institute": institute.lower(), "branch": branch.lower(), "semester": semester.lower()})

@router.post("/analyze_course")
async def analyze_course_endpoint(request: CourseScopeRequest):
    try:
        result = generate_topic_graph(request.institute, request.branch, request.semester, request.subject)
        return {"status": "success", "topic_graph": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing course: {str(e)}")

@router.post("/generate_study_plan")
async def generate_study_plan_endpoint(request: StudyPlanRequest):
    try:
        plan = generate_academic_schedule(
            institute=request.institute, branch=request.branch, semester=request.semester, subject=request.subject,
            exam_date=request.exam_date, daily_study_hours=request.daily_study_hours, preferred_difficulty=request.preferred_difficulty,
            weak_topics=request.weak_topics, strong_topics=request.strong_topics, events=request.events, student_id=request.student_id
        )
        return plan
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study plan: {str(e)}")

@router.post("/mark_day_progress")
async def mark_day_progress_endpoint(request: MarkProgressRequest):
    try:
        result = mark_day_progress(plan_id=request.plan_id, date_str=request.date, completed_task_ids=request.completed_tasks)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking progress: {str(e)}")

@router.post("/update_mastery")
async def update_mastery_endpoint(request: UpdateMasteryRequest):
    try:
        topic_data = update_topic_mastery(
            student_id=request.student_id, topic=request.topic, accuracy=request.accuracy,
            time_taken=request.time_taken, attempts=request.attempts
        )
        return {"status": "success", "topic_mastery": topic_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mastery_profile")
async def mastery_profile_endpoint(student_id: str, subject: Optional[str] = None):
    try:
        profile = get_mastery_profile(student_id=student_id, subject=subject)
        return {"status": "success", "profile": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/review_schedule")
async def review_schedule_endpoint(student_id: str, subject: Optional[str] = None):
    try:
        tasks = generate_review_tasks(student_id=student_id, subject=subject)
        return {"status": "success", "review_tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_concept_graph")
async def generate_concept_graph_endpoint(request: AnalyzeCourseRequest):
    try:
        graph = generate_concept_graph(request.institute, request.branch, request.semester, request.subject)
        return {"status": "success", "concept_graph": graph}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating concept graph: {str(e)}")

@router.post("/start_tutor_session")
async def start_tutor_session_endpoint(request: TutorSessionRequest):
    try:
        session = generate_tutor_session(
            request.student_id, request.institute, request.branch, request.semester, request.subject, request.topic
        )
        return {"status": "success", "session": session}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit_answers")
async def submit_answers_endpoint(request: TutorAnswerRequest):
    try:
        result = evaluate_tutor_answers(request.student_id, request.session_id, request.topic, request.answers)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student_analytics")
async def student_analytics_endpoint(student_id: str):
    try:
        return {"status": "success", "analytics": get_learning_analytics(student_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_practice")
async def generate_practice_request(request: PracticeSetRequest):
    try:
        return {"status": "success", "practice_set": generate_practice_set(
            request.student_id, request.institute, request.branch, request.semester, request.subject, request.topic, request.count
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_exam")
async def generate_exam_request(request: ExamGenerationRequest):
    try:
        return {"status": "success", "exam": generate_exam(
            request.student_id, request.institute, request.branch, request.semester, request.subject, request.exam_duration, request.question_count
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate_exam")
async def evaluate_exam_request(request: ExamEvaluationRequest):
    try:
        return {"status": "success", "results": evaluate_exam(
            request.student_id, request.subject, request.student_answers, request.answer_key
        )}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/institute_analytics")
async def institute_analytics_endpoint(topic: str):
    try:
        data = InstituteAnalytics.get_topic_analytics(topic)
        return {"status": "success", "analytics": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def notifications_endpoint(student_id: str, active_courses: str):
    try:
        course_ids = active_courses.split(",") if active_courses else []
        alerts = ReminderEngine.generate_alerts(student_id, course_ids)
        return {"status": "success", "notifications": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/course_timeline")
async def create_timeline_endpoint(timeline: CourseTimeline):
    try:
        timeline_manager.save_timeline(timeline)
        return {"status": "success", "message": f"Timeline for {timeline.course_id} securely registered."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
