# agents/comparison_agents.py

from typing import Dict, List
from ..core.data_models import AgentResult, PaperSections

class RelatedPaperComparisonAgent:
    """관련 논문 비교 분석 Agent (업로드 기반)"""
    
    def __init__(self):
        self.name = "RelatedPaperComparisonAgent"
    
    def analyze(self, user_paper: PaperSections, uploaded_papers: List[Dict]) -> AgentResult:
        """업로드된 관련 논문들과 비교 분석"""
        
        prompt = f"""
=== 사용자 논문 ===
Introduction: {user_paper.introduction[:500]}...
Related Work: {user_paper.related_work[:500]}...
Method: {user_paper.method[:500]}...

=== 업로드된 관련 논문들 ===
{self._format_uploaded_papers(uploaded_papers)}

=== 비교 분석 요청 ===
1. 커버리지 분석: 언급되지 않은 중요 연구 식별
2. 차별점 분석: 기존 연구와의 명확한 차이점
3. 포지셔닝 제안: 연구 계보상 위치
4. 인용 갭 분석: 누락된 중요 인용
        """
        
        mock_result = {
            "scores": {
                "관련연구 커버리지": 3.4,
                "차별점 명확성": 3.8,
                "포지셔닝 적절성": 3.6
            },
            "findings": [
                "최근 3년 내 주요 연구 2편 누락",
                "기존 연구와의 성능 비교 부족", 
                "해당 분야 survey 논문 미인용"
            ],
            "suggestions": [
                "Smith et al. (2023) 연구 추가 인용 권장",
                "성능 비교 테이블에 baseline 추가",
                "Related Work 구성 재정리 필요"
            ]
        }
        
        return AgentResult(
            agent_name=self.name,
            scores=mock_result["scores"],
            findings=mock_result["findings"],
            suggestions=mock_result["suggestions"],
            analysis_details=mock_result
        )
    
    def _format_uploaded_papers(self, papers: List[Dict]) -> str:
        """업로드된 논문들 포맷팅"""
        formatted = []
        for i, paper in enumerate(papers[:5]):  # 최대 5편만 표시
            formatted.append(f"논문 {i+1}: {paper.get('title', 'Unknown')} ({paper.get('year', 'N/A')})")
        return "\n".join(formatted)
