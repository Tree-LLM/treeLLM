# agents/usenix_agents.py

from typing import Dict
from .base_agent import BaseAgent
from ..core.data_models import AgentResult
from ..core.guideline_manager import GuidelineManager

class OriginalityAgent(BaseAgent):
    """독창성 분석 Agent"""
    
    def __init__(self, guideline_manager: GuidelineManager):
        super().__init__("OriginalityAgent", guideline_manager)
    
    def analyze(self, sections: Dict[str, str]) -> AgentResult:
        guidelines = self.guideline_manager.get_guidelines_for_agent("originality")
        prompt = self._create_base_prompt(sections, guidelines)
        
        # 실제 구현에서는 LLM API 호출
        # result = llm_api.call(prompt)
        
        # 예시 결과 (실제로는 LLM 응답을 파싱)
        mock_result = {
            "scores": {
                "문제 정의 명확성": 4.2,
                "기존 기술 한계 설명": 3.8,
                "아이디어 중요성": 4.0,
                "기존 연구와 차별성": 3.5
            },
            "findings": [
                "문제 정의가 비교적 명확하나 구체적 예시 부족",
                "기존 기술 한계 설명에서 정량적 근거 필요",
                "차별점이 추상적으로 표현됨"
            ],
            "suggestions": [
                "Before: '기존 방법의 한계가 있다' → After: '기존 방법은 X 상황에서 Y% 성능 저하를 보인다'",
                "구체적 사례나 수치를 통한 문제 정의 보강 필요",
                "차별점을 기능적, 성능적 측면에서 구체화"
            ]
        }
        
        return AgentResult(
            agent_name=self.name,
            scores=mock_result["scores"],
            findings=mock_result["findings"], 
            suggestions=mock_result["suggestions"],
            analysis_details=mock_result
        )

class LessonExtractionAgent(BaseAgent):
    """교훈 추출 분석 Agent"""
    
    def __init__(self, guideline_manager: GuidelineManager):
        super().__init__("LessonExtractionAgent", guideline_manager)
    
    def analyze(self, sections: Dict[str, str]) -> AgentResult:
        guidelines = self.guideline_manager.get_guidelines_for_agent("lessons")
        prompt = self._create_base_prompt(sections, guidelines)
        
        mock_result = {
            "scores": {
                "교훈 명확성": 3.5,
                "일반적 적용가능성": 3.8,
                "전제 조건 명시": 2.9,
                "결론의 논리성": 4.1
            },
            "findings": [
                "구체적 교훈 도출이 부족함",
                "전제 조건이 명시적으로 언급되지 않음",
                "일반화 가능성에 대한 논의 필요"
            ],
            "suggestions": [
                "구체적이고 실행 가능한 교훈 명시",
                "결론의 유효 조건과 전제 사항 명확화",
                "다른 도메인 적용 가능성 논의 추가"
            ]
        }
        
        return AgentResult(
            agent_name=self.name,
            scores=mock_result["scores"],
            findings=mock_result["findings"],
            suggestions=mock_result["suggestions"], 
            analysis_details=mock_result
        )

class AssumptionAgent(BaseAgent):
    """가정사항 분석 Agent"""
    
    def __init__(self, guideline_manager: GuidelineManager):
        super().__init__("AssumptionAgent", guideline_manager)
    
    def analyze(self, sections: Dict[str, str]) -> AgentResult:
        prompt = f"""
=== 가정사항 분석 가이드라인 ===
- 명시적/암시적 가정 식별
- 가정의 합리성 평가  
- 가정 위배시 영향 분석
- 전제 조건 명확화

{self._create_base_prompt(sections, "")}
        """
        
        mock_result = {
            "scores": {
                "가정 명시성": 3.2,
                "가정 합리성": 4.0,
                "위험성 인식": 3.6
            },
            "findings": [
                "데이터 분포에 대한 암시적 가정 존재",
                "실험 환경의 이상적 조건 가정",
                "일부 가정의 현실성 검토 필요"
            ],
            "suggestions": [
                "데이터 분포 가정을 명시적으로 기술",
                "가정 위배시 성능 영향 분석 추가",
                "현실적 제약 조건 고려 방안 제시"
            ]
        }
        
        return AgentResult(
            agent_name=self.name,
            scores=mock_result["scores"],
            findings=mock_result["findings"],
            suggestions=mock_result["suggestions"],
            analysis_details=mock_result
        )
