[Backend architecture for exambud.txt](https://github.com/user-attachments/files/25802021/Backend.architecture.for.exambud.txt)
ACADEMIC INTELLIGENCE PLATFORM
Backend Architecture Overview
-----------------------------

This document describes the architecture of the backend powering the Academic Intelligence Platform. The system is designed to ingest educational materials, build structured knowledge representations, and provide personalized academic assistance through retrieval-augmented AI workflows.

The backend integrates multimodal ingestion, hybrid retrieval, knowledge graphs, adaptive learning state tracking, and study planning engines into a unified API platform.

---

1. System Overview

---

The backend is organized into modular layers:

Client / Frontend
↓
FastAPI API Layer
↓
Service Layer
↓
Core Engines
• Ingestion Engine
• Retrieval Engine (Hybrid RAG)
• Intelligence Engine
• Planning Engine
↓
Vector Database + Local Data Storage
↓
LLM Generation Layer

The platform exposes its functionality through REST endpoints that allow students or institutions to upload materials, query course knowledge, generate study plans, practice questions, and analytics.

---

2. API Layer

---

The API layer is implemented using FastAPI.

Responsibilities:
• Request validation
• Endpoint routing
• Response formatting
• OpenAPI documentation generation
• Communication with backend service modules

Primary API endpoints include:

/upload
/query
/generate_study_plan
/generate_practice
/generate_exam
/evaluate_exam
/update_mastery
/student_analytics
/institute_analytics
/notifications
/course_timeline

These endpoints allow external clients or UI applications to interact with the academic intelligence engine.

---

3. Universal Knowledge Ingestion Engine

---

The ingestion engine converts academic materials into structured text suitable for vector indexing.

Supported formats:

Documents
• PDF (PyMuPDF)
• PPTX (python-pptx)
• DOCX (python-docx)
• TXT
• CSV

Images
• OCR using Tesseract

Audio
• Speech transcription using Whisper

Video
• Audio extraction using FFmpeg
• Speech transcription via Whisper
• Frame extraction
• OCR slide detection
• Speech + slide text merging

Processing pipeline:

File Upload
↓
Content Extraction
↓
Text Chunking
↓
Embedding Generation
↓
Vector Database Storage

All processed content is stored along with metadata describing the course context.

---

4. Embedding & Vectorization

---

Extracted text chunks are converted into vector embeddings.

Embedding model:

sentence-transformers
all-MiniLM-L6-v2

Each chunk is stored with metadata:

• institute
• branch
• semester
• subject
• topic
• lecture_number
• timestamp (for lecture materials)

Vector storage is handled by:

ChromaDB

This allows fast semantic similarity search across large educational corpora.

---

5. Hybrid Retrieval Engine (RAG)

---

The platform uses a hybrid retrieval strategy to maximize answer accuracy.

Retrieval pipeline:

User Query
↓
Query Rewriting
↓
Vector Similarity Search (ChromaDB)
↓
Lexical Search (BM25)
↓
Result Merging
↓
Cross-Encoder Reranking
↓
Top Context Chunks

Technologies used:

Vector Search
ChromaDB

Lexical Search
rank_bm25

Reranking Model
BAAI bge-reranker-base

This hybrid strategy ensures both semantic and keyword relevance.

---

6. Retrieval-Augmented Generation Layer

---

After retrieving relevant context, the system constructs prompts for the language model.

Input:

• user query
• retrieved context chunks

LLM options include:

Local models
• FLAN-T5

External APIs
• OpenAI
• Claude
• Mistral

The model produces structured responses containing:

• answer
• context citations
• supporting knowledge

---

7. Knowledge Graph System

---

The backend maintains structured representations of academic knowledge.

Topic Dependency Graph

Represents prerequisite relationships between topics.

Example:

Processes
↓
Deadlocks
↓
Deadlock Prevention

Concept Graph

Breaks topics into atomic concepts.

Example:

Deadlock
• mutual_exclusion
• hold_and_wait
• no_preemption
• circular_wait

Each concept node stores metadata such as:

• difficulty
• mastery score
• practice frequency

---

8. Student Learning State Engine

---

The system tracks each student's learning progress.

Student memory is stored locally:

data/memory_cache/{student_id}.json

Stored data includes:

• concept mastery scores
• practice history
• study progress
• weak concept tracking

Mastery scoring rules:

Correct answer → +0.05
Incorrect answer → −0.02

Scores are clamped between:

0.0 – 1.0

Spaced repetition decay is also applied to prevent forgotten concepts.

---

9. Academic Scheduling Engine

---

The scheduling engine generates personalized study plans.

Inputs:

• exam date
• daily study hours
• topic difficulty
• concept dependencies
• student mastery

Planner rules include:

• priority weighting
• deadline protection
• carry-over scheduling
• revision buffers
• emergency compression if time is insufficient

Output:

Structured daily study schedules including:

• topics
• revision sessions
• practice blocks

---

10. Practice & Exam Generation Engine

---

The platform can generate practice questions and exam simulations.

Question types include:

• multiple choice
• short answer
• concept checks
• full mock exams

Generation pipeline:

Weak Concepts
↓
Retrieve Context
↓
LLM Generates Questions
↓
Attach Concept Tags

Evaluation of answers updates student mastery scores.

---

11. Analytics Layer

---

The analytics subsystem provides insights for both students and institutions.

Student Analytics

• mastery profile
• weak concepts
• exam readiness score
• practice statistics

Institution Analytics

Aggregated cohort metrics:

• average mastery
• concept difficulty heatmaps
• student performance trends

---

12. Notification System

---

The notification engine monitors deadlines and learning progress.

Possible alerts include:

• assignment due reminders
• missed study goals
• revision recommendations
• upcoming exam warnings

---

13. Data Storage

---

Vector Database

ChromaDB

Student Memory

JSON cache files

Uploaded Materials

data/uploads directory

---

14. Performance Characteristics

---

Typical CPU-based execution times:

Embedding generation
~1–2 seconds

Vector retrieval
<100 ms

Reranking
~1–2 seconds

Local LLM generation
~15–20 seconds

Using external LLM APIs typically reduces total response latency to:

2–4 seconds.

---

15. Scalability Design

---

The architecture supports future scaling through:

• background task workers
• distributed vector databases
• external LLM APIs
• horizontal API scaling
• asynchronous ingestion pipelines

Heavy tasks such as video processing run asynchronously to avoid blocking the API.

---

## Summary

The backend functions as a complete academic intelligence engine capable of:

• ingesting multimodal educational content
• performing hybrid knowledge retrieval
• generating contextual answers
• tracking concept-level mastery
• creating personalized study schedules
• generating practice and exams
• providing institutional learning analytics

All functionality is exposed through a modular REST API, making the system ready for frontend integration and institutional deployment.
