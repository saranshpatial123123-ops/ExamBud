import os
import shutil
import re

base_dir = r"w:\ExamBud\ai-study-engine\backend"

moves = {
    "database.py": "database/core.py",
    "ingestion.py": "ingestion/ingestion.py",
    "extractors.py": "ingestion/extractors.py",
    "embeddings.py": "embeddings/embeddings.py",
    "retrieval.py": "retrieval/retrieval.py",
    "hybrid_retrieval.py": "retrieval/hybrid_retrieval.py",
    "query_rewriter.py": "retrieval/query_rewriter.py",
    "reranker.py": "retrieval/reranker.py",
    "rag.py": "rag/rag.py",
    "concept_graph.py": "knowledge_graph/concept_graph.py",
    "topic_graph.py": "knowledge_graph/topic_graph.py",
    "academic_planner.py": "planning/academic_planner.py",
    "study_planner.py": "planning/study_planner.py",
    "adaptive_tutor.py": "intelligence/adaptive_tutor.py",
    "mastery_engine.py": "intelligence/mastery_engine.py",
    "practice_engine.py": "intelligence/practice_engine.py",
    "learning_analytics.py": "intelligence/learning_analytics.py",
    "exam_simulator.py": "intelligence/exam_simulator.py",
    "difficulty_controller.py": "intelligence/difficulty_controller.py",
    "spaced_repetition.py": "intelligence/spaced_repetition.py"
}

# Reverse map original module names to new module paths
module_map = {
    "database": "backend.database.core",
    "ingestion": "backend.ingestion.ingestion",
    "extractors": "backend.ingestion.extractors",
    "embeddings": "backend.embeddings.embeddings",
    "retrieval": "backend.retrieval.retrieval",
    "hybrid_retrieval": "backend.retrieval.hybrid_retrieval",
    "query_rewriter": "backend.retrieval.query_rewriter",
    "reranker": "backend.retrieval.reranker",
    "rag": "backend.rag.rag",
    "concept_graph": "backend.knowledge_graph.concept_graph",
    "topic_graph": "backend.knowledge_graph.topic_graph",
    "academic_planner": "backend.planning.academic_planner",
    "study_planner": "backend.planning.study_planner",
    "adaptive_tutor": "backend.intelligence.adaptive_tutor",
    "mastery_engine": "backend.intelligence.mastery_engine",
    "practice_engine": "backend.intelligence.practice_engine",
    "learning_analytics": "backend.intelligence.learning_analytics",
    "exam_simulator": "backend.intelligence.exam_simulator",
    "difficulty_controller": "backend.intelligence.difficulty_controller",
    "spaced_repetition": "backend.intelligence.spaced_repetition",
    "config": "backend.config"
}

# 1. Move files
for old_name, new_path in moves.items():
    old_full = os.path.join(base_dir, old_name)
    new_full = os.path.join(base_dir, new_path.replace("/", os.sep))
    if os.path.exists(old_full):
        os.makedirs(os.path.dirname(new_full), exist_ok=True)
        shutil.move(old_full, new_full)
        print(f"Moved {old_name} -> {new_path}")

# 2. Fix imports in all python files recursively
def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    # Replace relative imports "from .X import Y"
    def replacer(match):
        module_name = match.group(1)
        if module_name in module_map:
            return f"from {module_map[module_name]} import {match.group(2)}"
        return match.group(0) # unchanged

    new_content = re.sub(r"from\s+\.(\w+)\s+import\s+(.+)", replacer, new_content)
    
    # Optional: some might use import .module, though usually not in this codebase

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed imports in {filepath}")

for root, _, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".py"):
            process_file(os.path.join(root, file))

print("Refactoring complete.")
