# core/section_extractor.py

from typing import Dict
from .data_models import PaperSections

class SectionExtractor:
    """논문 섹션 추출 관리 클래스"""
    
    # Agent별 필요 섹션 매핑
    AGENT_SECTION_MAPPING = {
        "OriginalityAgent": [1, 2],           # Introduction + Related Work
        "ContributionSignificanceAgent": "전체",  # 모든 섹션
        "RelatedWorkCoverageAgent": [2],       # Related Work만
        "ResearchGapAgent": [2],              # Related Work만
        "LessonExtractionAgent": [6],         # Conclusion만
        "AssumptionAgent": [3, 4],            # Method + Experiments
        "DesignChoiceAgent": [3, 4],          # Method + Experiments
        "ContextSensitivityAgent": [2],        # Related Work만
        "FocusAgent": [1, 2],                 # Introduction + Related Work
        "PresentationAgent": [1, 3, 4],       # Introduction + Method + Experiments
        "WritingStyleAgent": "전체"            # 모든 섹션
    }
    
    @classmethod
    def extract_sections_for_agent(cls, paper_sections: PaperSections, agent_name: str) -> Dict[str, str]:
        """Agent별로 필요한 섹션만 추출"""
        mapping = cls.AGENT_SECTION_MAPPING.get(agent_name, "전체")
        
        all_sections = {
            1: ("introduction", paper_sections.introduction),
            2: ("related_work", paper_sections.related_work), 
            3: ("method", paper_sections.method),
            4: ("experiments", paper_sections.experiments),
            5: ("discussion", paper_sections.discussion),
            6: ("conclusion", paper_sections.conclusion)
        }
        
        if mapping == "전체":
            return {name: content for _, (name, content) in all_sections.items()}
        else:
            return {all_sections[i][0]: all_sections[i][1] for i in mapping}
