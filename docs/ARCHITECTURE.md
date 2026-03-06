# ExamBud Backend Architecture

ExamBud uses a modular backend architecture designed for scalability,
multimodal ingestion, and intelligent academic workflows.

------------------------------------------------------------------------

# High Level Architecture

Student Interface\
↓\
FastAPI API Layer\
↓\
Service Layer\
↓\
Academic Intelligence Engine\
↓\
Hybrid Retrieval Engine\
↓\
Vector Database\
↓\
Language Model

------------------------------------------------------------------------

# Core Backend Layers

## API Layer

Handles all HTTP requests.

Responsibilities: - file uploads - query processing - study planning
requests - analytics requests

Implemented with FastAPI.

Example endpoints:

/upload\
/query\
/generate_study_plan\
/generate_practice\
/generate_exam\
/update_mastery\
/student_analytics\
/institute_analytics

------------------------------------------------------------------------

## Ingestion Layer

Responsible for converting uploaded files into structured knowledge.

Supported formats:

-   pdf
-   pptx
-   docx
-   txt
-   csv
-   images
-   audio
-   video

Pipeline:

File Upload → Content Extraction → Text Chunking → Embeddings → Vector
Storage

------------------------------------------------------------------------

## Embedding Layer

Text chunks are converted into embeddings using:

sentence‑transformers\
all‑MiniLM‑L6‑v2

Embeddings represent semantic meaning of academic content.

------------------------------------------------------------------------

## Vector Database

Embeddings are stored in ChromaDB.

Each chunk includes metadata:

-   institute
-   branch
-   semester
-   subject
-   topic
-   lecture number

This allows scoped academic retrieval.

------------------------------------------------------------------------

## Hybrid Retrieval Engine

Retrieval combines semantic and lexical search.

Query\
↓\
Query Rewriting\
↓\
Vector Search\
↓\
BM25 Search\
↓\
Result Merge\
↓\
Cross Encoder Reranking\
↓\
Context Selection

Technologies used:

-   ChromaDB
-   rank_bm25
-   BAAI bge‑reranker

------------------------------------------------------------------------

## RAG Engine

Retrieved context is passed to a language model.

Query + Context → LLM → Response

Supported models:

-   FLAN‑T5 (local)
-   OpenAI
-   Claude
-   Mistral

------------------------------------------------------------------------

## Knowledge Graph System

### Topic Graph

Represents dependencies between academic topics.

Example: Processes → Deadlocks → Deadlock Prevention

### Concept Graph

Breaks topics into atomic learning units.

Deadlock\
├ mutual_exclusion\
├ hold_and_wait\
├ no_preemption\
└ circular_wait

------------------------------------------------------------------------

## Learning Intelligence Engine

Tracks student learning state.

Stored data includes:

-   mastery scores
-   practice history
-   weak concepts
-   study progress

Memory stored as:

data/memory_cache/{student_id}.json

------------------------------------------------------------------------

## Study Planning Engine

Generates personalized study schedules.

Inputs: - exam dates - student mastery - concept difficulty - topic
dependencies

Output: Daily schedule including topics, revision, and practice.

------------------------------------------------------------------------

## Analytics Engine

Provides insights for students and institutions.

Student analytics: - mastery profile - weak concepts - readiness score

Institution analytics: - concept difficulty heatmaps - cohort
performance - learning trends

------------------------------------------------------------------------

## Asynchronous Processing

Heavy workloads run asynchronously:

-   video ingestion
-   large data ingestion
-   analytics aggregation
