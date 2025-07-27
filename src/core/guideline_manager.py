# core/guideline_manager.py

from typing import Dict

class GuidelineManager:
    """가이드라인 관리 클래스"""
    
    def __init__(self):
        self.guidelines = self._load_guidelines()
    
    def _load_guidelines(self) -> Dict:
        """USENIX 및 기타 가이드라인 로드"""
        return {
            "usenix": {
                "original_ideas": {
                    "criteria": ["문제 정의 명확성", "기존 기술 한계 설명", "아이디어 중요성", "기존 연구와 차별성"],
                    "questions": [
                        "정확히 어떤 문제를 해결하려는 것인가?",
                        "기존 기술로는 왜 해결될 수 없었는가?", 
                        "논문으로 낼 만큼 충분히 중요한가?",
                        "기존 연구와 확연히 다른가?"
                    ],
                    "scoring_guide": {
                        "1": "매우 부족 - 근본적 문제 있음",
                        "2": "부족 - 상당한 개선 필요",
                        "3": "보통 - 일부 개선 필요", 
                        "4": "좋음 - 소폭 개선으로 충분",
                        "5": "우수 - USENIX 기준 충족"
                    }
                },
                "reality": {
                    "criteria": ["실제 구현 여부", "구현 완성도", "실용적 중요성", "현재 발표 가치"],
                    "questions": [
                        "실제로 구현된 것을 설명하고 있는가?",
                        "구현이 어떻게 사용되었고 실용적 중요성을 보여주는가?",
                        "구현되지 않았다면 지금 발표할 가치가 있는가?"
                    ]
                },
                "lessons": {
                    "criteria": ["교훈 명확성", "일반적 적용가능성", "전제 조건 명시", "결론의 논리성"],
                    "questions": [
                        "이 작업을 통해 무엇을 배웠는가?",
                        "이 교훈들은 얼마나 일반적으로 적용될 수 있는가?",
                        "결론이 기반하는 전제들이 명확히 밝혀져 있는가?"
                    ]
                }
            }
        }
    
    def get_guidelines_for_agent(self, agent_type: str) -> str:
        """Agent별 가이드라인 텍스트 생성"""
        if agent_type == "originality":
            gl = self.guidelines["usenix"]["original_ideas"]
        elif agent_type == "reality": 
            gl = self.guidelines["usenix"]["reality"]
        elif agent_type == "lessons":
            gl = self.guidelines["usenix"]["lessons"]
        else:
            return ""
            
        return f"""
=== 평가 기준 ===
{' / '.join(gl['criteria'])}

=== 핵심 질문 ===
{' | '.join(gl['questions'])}

=== 점수 가이드 ===
1점: 매우 부족, 2점: 부족, 3점: 보통, 4점: 좋음, 5점: 우수
        """
