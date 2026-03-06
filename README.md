# ExamBud

## AI-Powered Academic Intelligence Platform

ExamBud is an AI-powered academic intelligence platform that converts
raw academic materials into an interactive learning system.

The platform combines Retrieval Augmented Generation (RAG), hybrid
search, knowledge graphs, and adaptive learning to help students study
more effectively and help institutions improve academic outcomes.

------------------------------------------------------------------------

# Problem

Students face several challenges in modern education:

-   Information overload from lectures, notes, and assignments
-   Lack of personalized learning
-   Poor study planning before exams
-   Weak conceptual understanding
-   Limited feedback on learning progress

Traditional learning platforms simply store content but do not help
students understand or organize it effectively.

------------------------------------------------------------------------

# Solution

ExamBud builds an Academic Intelligence Engine capable of:

-   Understanding course materials
-   Answering student questions
-   Generating practice questions
-   Tracking concept mastery
-   Creating personalized study plans
-   Providing academic analytics

Institutions upload course material and ExamBud converts it into a
structured AI knowledge base.

------------------------------------------------------------------------

# Key Features

## Universal Knowledge Ingestion

Supports multiple academic formats.

Documents - PDF - PowerPoint - Word - Text files - CSV

Multimedia - Images - Audio lectures - Video lectures

Processing tools include PyMuPDF, python‑pptx, Tesseract OCR, Whisper
transcription, and FFmpeg video processing.

------------------------------------------------------------------------

## Hybrid Retrieval System

ExamBud combines semantic and keyword retrieval.

User Query\
↓\
Query Rewriting\
↓\
Vector Search (ChromaDB)\
↓\
BM25 Keyword Search\
↓\
Result Merging\
↓\
Cross Encoder Reranking\
↓\
Context Retrieval

------------------------------------------------------------------------

## Retrieval Augmented Generation

Query + Retrieved Context → Language Model → Answer + Sources

Supported models include FLAN‑T5 (local), OpenAI, Claude, and Mistral.

------------------------------------------------------------------------

## Personalized Study Planner

ExamBud automatically generates structured study schedules using:

-   exam dates
-   student mastery levels
-   concept difficulty
-   topic dependencies
-   available study hours

------------------------------------------------------------------------

## Practice and Exam Generation

ExamBud can generate:

-   MCQs
-   conceptual questions
-   short answer questions
-   full mock exams

Answers update concept mastery scores.

------------------------------------------------------------------------

# System Architecture Overview

Student Interface\
↓\
FastAPI Backend\
↓\
Academic Intelligence Engine\
↓\
Hybrid Retrieval System\
↓\
Vector Database (ChromaDB)\
↓\
Language Model Generation

------------------------------------------------------------------------
## Documentation

Detailed backend documentation:

- [Backend Architecture](docs/BACKEND_ARCHITECTURE.md)
- [Backend Features](docs/BACKEND_FEATURES.md)

-------------------------------------------------------------------------
© 2026 ExamBud. All rights reserved.
