from typing import List, Optional
from pydantic import BaseModel

class TopicNode(BaseModel):
    topic_name: str
    difficulty_score: float = 0.5
    prerequisites: List[str] = []
    related_topics: List[str] = []

class TopicDependencyGraph:
    def __init__(self):
        self._graph = {}
        
    def add_topic(self, topic: TopicNode):
        self._graph[topic.topic_name] = topic
        
    def get_topic(self, topic_name: str) -> Optional[TopicNode]:
        return self._graph.get(topic_name)
        
    def get_all_topics(self) -> List[TopicNode]:
        return list(self._graph.values())
        
    def get_prerequisites(self, topic_name: str) -> List[str]:
        topic = self.get_topic(topic_name)
        if not topic:
            return []
        return topic.prerequisites
        
    def validate_plan(self, planned_topics: List[str]) -> bool:
        """
        Ensures a list of planned topics respects prerequisite order.
        """
        seen = set()
        for t_name in planned_topics:
            topic = self.get_topic(t_name)
            if topic:
                for prereq in topic.prerequisites:
                    if prereq not in seen and prereq in planned_topics:
                        # Prerequisite was scheduled *after* this topic, or not at all
                        return False
            seen.add(t_name)
        return True

# Singleton instance for the application lifecycle
topic_graph = TopicDependencyGraph()

# Example seeding (can be replaced with dynamic extraction later)
topic_graph.add_topic(TopicNode(
    topic_name="Processes",
    difficulty_score=0.4,
    prerequisites=[],
    related_topics=["Threads"]
))
topic_graph.add_topic(TopicNode(
    topic_name="Threads",
    difficulty_score=0.5,
    prerequisites=["Processes"],
    related_topics=["Processes"]
))
topic_graph.add_topic(TopicNode(
    topic_name="Scheduling",
    difficulty_score=0.6,
    prerequisites=["Processes"],
    related_topics=["Resource Allocation"]
))
topic_graph.add_topic(TopicNode(
    topic_name="Deadlocks",
    difficulty_score=0.7,
    prerequisites=["Processes", "Resource Allocation"],
    related_topics=[]
))
