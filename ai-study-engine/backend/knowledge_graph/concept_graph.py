from typing import List, Optional
from pydantic import BaseModel

class ConceptNode(BaseModel):
    concept_id: str
    topic: str
    difficulty: float = 0.5  # Innate difficulty 0.0 to 1.0
    prerequisites: List[str] = []
    related_concepts: List[str] = []

class ConceptGraph:
    def __init__(self):
        self._graph = {}
        
    def add_concept(self, concept: ConceptNode):
        self._graph[concept.concept_id] = concept
        
    def get_concept(self, concept_id: str) -> Optional[ConceptNode]:
        return self._graph.get(concept_id)
        
    def get_concepts_for_topic(self, topic_name: str) -> List[ConceptNode]:
        return [c for c in self._graph.values() if c.topic == topic_name]

    def get_prerequisites(self, concept_id: str) -> List[str]:
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        return concept.prerequisites

# Singleton instance
concept_graph = ConceptGraph()

# Example Seeding
concept_graph.add_concept(ConceptNode(
    concept_id="mutual_exclusion",
    topic="Deadlocks",
    difficulty=0.3,
    prerequisites=[]
))
concept_graph.add_concept(ConceptNode(
    concept_id="hold_and_wait",
    topic="Deadlocks",
    difficulty=0.5,
    prerequisites=["mutual_exclusion"]
))
concept_graph.add_concept(ConceptNode(
    concept_id="no_preemption",
    topic="Deadlocks",
    difficulty=0.6,
    prerequisites=["mutual_exclusion"]
))
concept_graph.add_concept(ConceptNode(
    concept_id="circular_wait",
    topic="Deadlocks",
    difficulty=0.72,
    prerequisites=["mutual_exclusion", "hold_and_wait"]
))

def generate_concept_graph(institute: str, branch: str, semester: str, subject: str) -> dict:
    # Stub added to resolve missing import error
    return {"message": "Not implemented yet"}

def load_concept_graph(institute: str, branch: str, semester: str, subject: str) -> dict:
    # Stub added to resolve missing import error
    return {"message": "Not implemented yet"}
