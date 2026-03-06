import requests
import json
import time

base_url = "http://localhost:8000"

def test_ingestion():
    url = f"{base_url}/upload/"
    # Create a dummy test file content
    content = "This is a test document about deadlocks in operating systems. Deadlocks occur when multiple processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process."
    with open("test_doc.txt", "w", encoding="utf-8") as f:
        f.write(content)
        
    with open("test_doc.txt", "rb") as f:
        files = {"file": ("test_doc.txt", f, "text/plain")}
        data = {
            "institute": "TestInst",
            "branch": "TestBranch",
            "semester": "TestSem",
            "subject": "TestSubj",
            "topic": "Deadlocks",
            "lecture_number": 1
        }
        print(f"Testing Ingestion ({url})...")
        response = requests.post(url, files=files, data=data)
    try:
        res_json = response.json()
        print("Response:", json.dumps(res_json, indent=2))
        return res_json
    except Exception as e:
        print("Error decoding JSON from response:", response.text)
        return None

def test_rag():
    url = f"{base_url}/query"
    data = {
        "question": "What are deadlocks?",
        "institute": "TestInst",
        "branch": "TestBranch",
        "semester": "TestSem",
        "subject": "TestSubj"
    }
    print(f"\nTesting RAG Query ({url})...")
    response = requests.post(url, json=data)
    try:
        res_json = response.json()
        print("Response:", json.dumps(res_json, indent=2))
        return res_json
    except Exception as e:
        print("Error decoding JSON from response:", response.text)
        return None

def test_analyze():
    url = f"{base_url}/analyze_course"
    data = {
        "institute": "TestInst",
        "branch": "TestBranch",
        "semester": "TestSem",
        "subject": "TestSubj"
    }
    print(f"\nTesting Analyze ({url})...")
    response = requests.post(url, json=data)
    try:
        res_json = response.json()
        print("Response (First 500 chars):", json.dumps(res_json, indent=2)[:500])
        return res_json
    except Exception as e:
        print("Error decoding JSON from response:", response.text)
        return None

def test_planner():
    url = f"{base_url}/generate_study_plan"
    data = {
        "student_id": "test_student",
        "institute": "TestInst",
        "branch": "TestBranch",
        "semester": "TestSem",
        "subject": "TestSubj",
        "exam_date": "2026-05-01",
        "daily_study_hours": 3.0,
        "weak_topics": ["Deadlocks"]
    }
    print(f"\nTesting Study Planner ({url})...")
    response = requests.post(url, json=data)
    try:
        res_json = response.json()
        print("Response (First 500 chars):", json.dumps(res_json, indent=2)[:500])
        return res_json
    except Exception as e:
        print("Error decoding JSON from response:", response.text)
        return None

import sys
if __name__ == "__main__":
    with open("test_api_log.txt", "w", encoding="utf-8") as log_file:
        sys.stdout = log_file
        try:
            root_res = requests.get(f"{base_url}/").json()
            print("Root Endpoint:", root_res)
        except Exception as e:
            print("Failed to reach Root Endpoint.", e)
            
        res1 = test_ingestion()
        if res1 and res1.get("chunks", 0) != 0:
            import time
            time.sleep(1)
            test_rag()
        else:
            print("Ingestion returned 0 chunks stored or failed. RAG might fail if DB is empty.")
            
        test_analyze()    
        test_planner()
        sys.stdout = sys.__stdout__
