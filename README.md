
# 🚀 ExamBud


  <b>AI-Powered Academic Intelligence Platform</b><br>
  Transform raw academic content into an intelligent learning system


## ⚡ Overview

ExamBud is an **AI-powered academic intelligence platform** designed to bridge the gap between *content availability* and *actual understanding*.

Instead of acting as a passive storage system, ExamBud actively:

* Interprets academic material
* Structures knowledge
* Adapts to the student
* Continuously improves learning outcomes

It integrates **Retrieval Augmented Generation (RAG)**, **hybrid search**, and **adaptive learning systems** into a unified academic engine.

---

## ❌ Problem

Modern students are overwhelmed, not under-resourced.

Key issues:

* Massive volumes of unstructured content (notes, PPTs, recordings)
* No personalized guidance or adaptive learning
* Inefficient and reactive study habits
* Weak conceptual linking between topics
* Lack of measurable feedback on progress

Most platforms solve *access*, not *understanding*.

---

## ✅ Solution

ExamBud introduces an **Academic Intelligence Engine** that transforms static content into an interactive system.

It enables:

* Context-aware question answering
* Automatic knowledge structuring
* Intelligent practice generation
* Real-time mastery tracking
* Adaptive study planning

Institutions upload raw course material → ExamBud builds a **searchable, queryable knowledge system**.

---

## 🔥 Key Features

---

### 📥 Universal Knowledge Ingestion

Handles diverse academic inputs and converts them into structured knowledge.

**Supported Formats**

* PDF, PPT, Word, TXT, CSV
* Images (via OCR)
* Audio & video lectures

**Processing Pipeline**

* PyMuPDF → document parsing
* python-pptx → slide extraction
* Tesseract OCR → text from images
* Whisper → speech-to-text
* FFmpeg → video preprocessing

**Frontend Experience**

* Drag-and-drop uploads
* Live file previews
* Auto-generated summaries as cards
* Inline highlighting + annotation
* Lecture timeline synced with transcripts

---

### 🔍 Hybrid Retrieval System

Combines **semantic understanding + keyword precision** for accurate retrieval.

```
User Query
↓
Query Rewriting
↓
Vector Search (ChromaDB)
↓
BM25 Keyword Search
↓
Result Merging
↓
Cross-Encoder Reranking
↓
Final Context
```

**Why this matters**

* Semantic search alone misses exact terms
* Keyword search alone lacks understanding
  → Hybrid = best of both

**Frontend Experience**

* Smart search bar with real-time suggestions
* Query refinement and correction
* Filters (subject / topic / difficulty)
* Split interface:

  * Left → source documents
  * Right → AI response
* Highlighted matches in content

---

### 🤖 Retrieval Augmented Generation (RAG)

Ensures answers are **accurate, grounded, and explainable**.

```
Query + Context → LLM → Answer + Sources
```

**Supported Models**

* FLAN-T5 (local inference)
* OpenAI
* Claude
* Mistral

**Capabilities**

* Context-aware responses
* Source-backed answers
* Reduced hallucination

**Frontend Experience**

* Chat-based assistant
* Explanation modes:

  * Quick answer
  * Exam-ready
  * Deep explanation
* Follow-up question suggestions
* Save to notes / revision list

---

### 📅 Personalized Study Planner

Generates adaptive schedules based on multiple factors.

**Inputs**

* Exam deadlines
* Concept mastery
* Topic difficulty
* Dependency graphs
* Available study time

**System Behavior**

* Prioritizes weak + high-impact topics
* Adjusts schedule dynamically
* Balances workload intelligently

**Frontend Experience**

* Task cards with status:

  * Completed
  * In Progress
  * Incomplete
  * Deferred
* Daily “Today Focus” panel
* Smart rescheduling on missed tasks
* Visual workload distribution

---

### 📝 Practice & Exam Generation

Transforms knowledge into **active learning loops**.

**Generated Content**

* MCQs
* Conceptual questions
* Short answers
* Full-length mock exams

**Evaluation System**

* Tracks accuracy
* Updates mastery scores
* Identifies weak areas

**Frontend Experience**

* Exam simulator (timed interface)
* Instant feedback with explanations
* Performance analytics dashboard
* Retry weak topics
* Adaptive difficulty progression

---

### 📊 Academic Dashboard & Progress Visualization

Turns abstract learning into **visual feedback**.

**Core Elements**

* Radial mastery gauges per subject
* Color-coded performance levels
* Central focus module
* Integrated study timer

**Why it works**

* Immediate feedback → higher engagement
* Visual progress → motivation
* Time tracking → discipline

---

### 🎯 Navigation & UX Design

Built for **focus, speed, and engagement**.

**Design System**

* Dark theme (low eye strain)
* Glassmorphism UI elements
* Smooth micro-interactions

**Navigation**

* Sidebar / icon-based quick access
* Sections:

  * Dashboard
  * Tasks
  * Calendar
  * Notes
  * Profile
  * Settings

**Experience Goals**

* Zero friction navigation
* High visual clarity
* Continuous engagement

---

## 🏗️ System Architecture

```
Student Interface
        ↓
FastAPI Backend
        ↓
Academic Intelligence Engine
        ↓
Hybrid Retrieval System
        ↓
Vector Database (ChromaDB)
        ↓
Language Model (LLM Layer)
```

---

## 🧠 Core Technologies

* FastAPI (backend)
* ChromaDB (vector storage)
* BM25 (keyword retrieval)
* Cross-Encoder (reranking)
* LLM APIs (OpenAI / Claude / Mistral)
* Whisper + OCR pipelines

---

## 📚 Documentation

* Backend Architecture → ai-study-engine/docs/BACKEND_ARCHITECTURE.md
* Backend Features → ai-study-engine/docs/BACKEND_FEATURES.md
* Dashboard Frontend Architecture-> frontend_dashboard/docs/architecture.md
* Dashboard Frontend Features-> frontend_dashboard/docs/dashboard_features.md

---

## 🧠 Vision

ExamBud aims to evolve into a **complete academic intelligence system**:

* Understands how students learn
* Adapts in real-time
* Optimizes study efficiency
* Improves academic performance at scale

---

## ⭐ Why ExamBud

Most platforms:
→ store content

ExamBud:
→ understands, organizes, and teaches

---
© 2026 ExamBud. All rights reserved.
