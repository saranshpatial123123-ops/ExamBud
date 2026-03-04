import os
import glob
from backend.learning_state.student_memory import StudentMemory, CACHE_DIR
from backend.knowledge_graph.concept_graph import concept_graph
from backend.utils.logging_utils import get_logger
from typing import Dict, Any

logger = get_logger("InstituteAnalytics")

class InstituteAnalytics:
    @classmethod
    def get_topic_analytics(cls, topic_name: str) -> Dict[str, Any]:
        """
        Aggregates mastery data across ALL active local student records for a specific Macro Topic.
        """
        # 1. Resolve which granular concepts belong to this Macro topic
        relevant_concepts = concept_graph.get_concepts_for_topic(topic_name)
        concept_ids = [c.concept_id for c in relevant_concepts]
        
        if not concept_ids:
            logger.warning(f"Analytics query failed: Focus topic '{topic_name}' resolved to 0 mapped concepts.")
            return {"error": "Topic contains no mapped verifiable concepts."}
            
        # 2. Open all local cache profiles to parse massive matrix states 
        profile_files = glob.glob(os.path.join(CACHE_DIR, "*.json"))
        
        total_students = len(profile_files)
        logger.info(f"Extracting macro-analytics for '{topic_name}' over {total_students} cached student matrices.")
        if total_students == 0:
            return {"message": "No student metrics available yet."}
            
        students_struggling = 0
        overall_mastery_sum = 0
        concept_sum = {c_id: 0.0 for c_id in concept_ids}
        concept_counts = {c_id: 0 for c_id in concept_ids}
        
        for f in profile_files:
            student_id = os.path.basename(f).replace(".json", "")
            profile = StudentMemory.load_profile(student_id)
            masteries = profile.get("concept_mastery", {})
            
            # Aggregate the student's mastery across the topic
            student_topic_sum = 0
            student_topic_count = 0
            
            for c_id in concept_ids:
                if c_id in masteries:
                    val = masteries[c_id]
                    student_topic_sum += val
                    concept_sum[c_id] += val
                else: 
                    # Default neutral rating assigned
                    val = 0.5 
                    student_topic_sum += val
                    concept_sum[c_id] += val
                    
                student_topic_count += 1
                concept_counts[c_id] += 1
                
            student_avg = student_topic_sum / student_topic_count if student_topic_count > 0 else 0.5
            overall_mastery_sum += student_avg
            
            # Sub-40% mastery triggers a struggling flag
            if student_avg < 0.4:
                students_struggling += 1
                
        # 3. Final Computation Reporting
        avg_mastery = overall_mastery_sum / total_students
        
        # Difficulty Heatmap -> Inverse of Mastery. (If avg mastery is 0.2, difficulty is High/0.8)
        heatmap = {}
        for c_id in concept_ids:
            c_avg = concept_sum[c_id] / concept_counts[c_id] if concept_counts[c_id] > 0 else 0.5
            heatmap[c_id] = round(1.0 - c_avg, 3) 
            
        return {
            "topic": topic_name,
            "average_mastery": round(avg_mastery, 3),
            "total_students_measured": total_students,
            "students_struggling": students_struggling,
            "concept_difficulty_heatmap": heatmap
        }
