# agents/base_agent.py

from typing import Dict
from ..core.data_models import AgentResult
from ..core.guideline_manager import GuidelineManager

class BaseAgent:
    """기본 Agent 클래스"""
    
    def __init__(self, name: str, guideline_manager: GuidelineManager):
        self.name = name
        self.guideline_manager = guideline_manager
    
    def analyze(self, sections: Dict[str, str]) -> AgentResult:
        """섹션 분석 (하위 클래스에서 구현)"""
        raise NotImplementedError
    
    def _create_base_prompt(self, sections: Dict[str, str], guidelines: str) -> str:
        """기본 프롬프트 생성"""
        sections_text = "\n\n".join([f"=== {name.upper()} ===\n{content}" 
                                    for name, content in sections.items() if content.strip()])
        
        return f"""
{guidelines}

=== 분석 대상 논문 섹션 ===
{sections_text}

=== 분석 요청 ===
위 가이드라인 기준으로 논문을 평가하고 다음 형식으로 답해주세요:

1. 점수 평가: 각 기준별로 1-5점 점수
2. 주요 발견사항: 구체적인 강점과 약점
3. 개선 제안: Before/After 형식의 구체적 수정 제안
4. 우선순위: 가장 시급한 개선사항 3가지

JSON 형식으로 구조화해서 답해주세요.
        """
