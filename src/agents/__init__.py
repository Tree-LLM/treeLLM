# agents/__init__.py

from .base_agent import BaseAgent
from .usenix_agents import OriginalityAgent, LessonExtractionAgent, AssumptionAgent
from .comparison_agents import RelatedPaperComparisonAgent

__all__ = [
    'BaseAgent',
    'OriginalityAgent',
    'LessonExtractionAgent', 
    'AssumptionAgent',
    'RelatedPaperComparisonAgent'
]
