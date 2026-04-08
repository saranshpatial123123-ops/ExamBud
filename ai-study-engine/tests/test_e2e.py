import requests
import json
import time

BASE_URL = "http://localhost:8000"

def log_time(start_time, end_time, name):
    duration = end_time - start_time
    print(f"[{name}] Response time: {duration:.2f} seconds")
    return duration

def run_tests():
    report = {
        "ingestion_success": False,
        "retrieval_success": False,
        "study_plan_success": False,
        "practice_success": False,
        "average_retrieval_time": 0.0
    }
    
    # 1. SERVER CHECK
    try:
        res = requests.get(f"{BASE_URL}/")
        print("Server check:", res.json())
    except Exception as e:
        print("Server not reachable. Exiting.", e)
        return
        
    print("\n--- STEP 1: INGESTION ---")
    content = "Deadlocks occur in operating systems when multiple processes wait indefinitely for resources held by each other.\n\nFour necessary conditions for deadlock are:\n\n1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait\n\nDeadlocks can be prevented by breaking one of these conditions."
    with open("test_os_notes.txt", "w", encoding="utf-8") as f:
        f.write(content)
        
    start_t = time.time()
    with open("test_os_notes.txt", "rb") as f:
        files = {"file": ("test_os_notes.txt", f, "text/plain")}
        data = {
            "institute": "TestUniversity",
            "branch": "CSE",
            "semester": "4",
            "subject": "Operating Systems",
            "topic": "Deadlocks",
            "lecture_number": 1
        }
        res = requests.post(f"{BASE_URL}/upload/", files=files, data=data)
    log_time(start_t, time.time(), "Ingestion")
    
    try:
        res_json = res.json()
        print("Ingestion Result:", json.dumps(res_json, indent=2))
        if res_json.get("chunks", 0) > 0 or res_json.get("chunks", 0) == -1: # -1 if already ingested
             report["ingestion_success"] = True
    except Exception as e:
        print("Ingestion Failed. Response:", res.text)
        
    # Also analyze course so planner works
    print("\n--- ANALYZE COURSE (Dependency for planner) ---")
    data = {
        "institute": "TestUniversity",
        "branch": "cse",
        "semester": "4",
        "subject": "operating systems"
    }
    res = requests.post(f"{BASE_URL}/analyze_course", json=data)
    print("Analyze result (First 200 chars):", res.text[:200])
        
    print("\n--- STEP 2: RETRIEVAL ---")
    queries = [
        "What is a deadlock?",
        "What are the four conditions for deadlock?",
        "Explain circular wait."
    ]
    
    retrieval_times = []
    success_count = 0
    
    for i, q in enumerate(queries):
        start_t = time.time()
        res = requests.post(f"{BASE_URL}/query", json={
            "question": q,
            "institute": "testuniversity",
            "branch": "cse",
            "semester": "4",
            "subject": "operating systems"
        })
        rt = log_time(start_t, time.time(), f"Query {i+1}")
        retrieval_times.append(rt)
        
        try:
            rjson = res.json()
            print(f"Q: {q}")
            print(f"A: {rjson.get('answer', 'NO ANSWER')}")
            print(f"Sources: {len(rjson.get('sources', []))} chunks retrieved\n")
            if "answer" in rjson and rjson["answer"] and "Error" not in rjson["answer"]:
                success_count += 1
        except Exception as e:
            print("Query Failed. Response:", res.text)
            
    if success_count == len(queries):
        report["retrieval_success"] = True
    if retrieval_times:
        report["average_retrieval_time"] = sum(retrieval_times) / len(retrieval_times)

    print("\n--- STEP 3: STUDY PLAN ---")
    start_t = time.time()
    res = requests.post(f"{BASE_URL}/generate_study_plan", json={
        "institute": "testuniversity",
        "branch": "cse",
        "semester": "4",
        "subject": "operating systems",
        "exam_date": "2026-05-01",
        "daily_study_hours": 2.0
    })
    log_time(start_t, time.time(), "Study Plan")
    try:
        rjson = res.json()
        print("Plan Schedule Length:", len(rjson.get("schedule", [])))
        if "schedule" in rjson and len(rjson["schedule"]) > 0:
            report["study_plan_success"] = True
    except Exception as e:
        print("Plan Failed. Response:", res.text)
        
    print("\n--- STEP 4: PRACTICE ENGINE ---")
    start_t = time.time()
    res = requests.post(f"{BASE_URL}/generate_practice", json={
        "student_id": "test_student",
        "institute": "testuniversity",
        "branch": "cse",
        "semester": "4",
        "subject": "operating systems",
        "topic": "Deadlocks",
        "count": 3
    })
    log_time(start_t, time.time(), "Practice Engine")
    try:
        rjson = res.json()
        print("Practice Set Snippet:", str(rjson)[:200])
        if "practice_set" in rjson:
            report["practice_success"] = True
    except Exception as e:
        print("Practice Failed. Response:", res.text)

    print("\n\n--- FINAL E2E REPORT ---")
    print(json.dumps(report, indent=2))
    print("Backend Stable:", all([report["ingestion_success"], report["retrieval_success"], report["study_plan_success"], report["practice_success"]]))

if __name__ == "__main__":
    import sys
    with open("e2e_results.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        run_tests()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
