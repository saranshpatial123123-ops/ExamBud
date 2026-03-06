# ExamBud Backend Features

This document describes the capabilities implemented in the ExamBud
backend system.

------------------------------------------------------------------------

# Universal Knowledge Ingestion

The system can ingest multiple academic content types.

Supported formats:

Documents - PDF - PPTX - DOCX - TXT - CSV

Media - Images - Audio lectures - Video lectures

Extraction tools:

-   PyMuPDF
-   python‑pptx
-   python‑docx
-   Tesseract OCR
-   Whisper transcription
-   FFmpeg processing

All extracted content is converted into structured text chunks.

------------------------------------------------------------------------

# Multimodal Video Processing

Video lectures are processed through multiple stages:

Video\
↓\
Audio Extraction\
↓\
Speech Transcription\
↓\
Frame Extraction\
↓\
Slide OCR\
↓\
Transcript + Slide Merge\
↓\
Embedding Generation

This allows the system to understand both spoken content and visual
slide content.

------------------------------------------------------------------------

# Hybrid Retrieval

ExamBud retrieves academic knowledge using hybrid search.

Components:

-   vector search
-   keyword search
-   cross encoder reranking

Technologies used:

-   ChromaDB
-   sentence‑transformers
-   rank_bm25
-   bge‑reranker

------------------------------------------------------------------------

# Retrieval Augmented Generation

ExamBud answers questions using retrieved academic context.

Student Query\
↓\
Retrieve Context\
↓\
Language Model Generation\
↓\
Answer with supporting context

------------------------------------------------------------------------

# Concept Mastery Tracking

Each student has concept‑level mastery scores.

Example:

mutual_exclusion : 0.82\
hold_and_wait : 0.44\
circular_wait : 0.21

Mastery update rules:

Correct answer → +0.05\
Incorrect answer → −0.02

Score range: 0.0 -- 1.0

------------------------------------------------------------------------

# Adaptive Study Planning

ExamBud generates personalized study schedules.

Inputs:

-   exam date
-   study hours per day
-   concept difficulty
-   mastery levels

Output example:

Day 1 → Topic A\
Day 2 → Topic B\
Day 3 → Revision

------------------------------------------------------------------------

# Practice and Exam Generation

The system generates:

-   MCQs
-   conceptual questions
-   short answers
-   mock exams

Questions are tagged with concepts so mastery can be updated after
answering.

------------------------------------------------------------------------

# Student Analytics

Tracks student learning progress including:

-   mastery profile
-   weak concepts
-   practice performance
-   readiness score

------------------------------------------------------------------------

# Institutional Analytics

Provides aggregated insights:

-   average mastery across students
-   concept difficulty heatmaps
-   cohort learning trends

------------------------------------------------------------------------

# Asynchronous Processing

Background tasks handle heavy workloads such as:

-   video processing
-   large ingestion jobs
-   analytics computation
