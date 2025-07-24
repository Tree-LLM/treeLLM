# tests/test_agents.py

import pytest
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import PaperSections, GuidelineManager
from src.agents import OriginalityAgent, LessonExtractionAgent
from utils.llm_interface import MockLLMInterface

class TestAgents:
    """Agent 테스트 클래스"""
    
    def setup_method(self):
        """테스트 셋업"""
        self.guideline_manager = GuidelineManager()
        self.sample_paper = PaperSections(
            introduction="본 연구는 자연어 처리의 중요한 문제를 다룹니다.",
            related_work="기존 연구들은 다음과 같은 접근을 시도했습니다.",
            method="제안하는 방법은 Transformer 기반입니다.",
            experiments="실험은 3개 데이터셋에서 수행되었습니다.",
            discussion="결과 분석에 따르면 우수한 성능을 보입니다.",
            conclusion="결론적으로 본 연구는 의미있는 기여를 합니다."
        )
    
    def test_originality_agent(self):
        """독창성 Agent 테스트"""
        agent = OriginalityAgent(self.guideline_manager)
        
        # 테스트용 섹션 (Introduction + Related Work)
        sections = {
            "introduction": self.sample_paper.introduction,
            "related_work": self.sample_paper.related_work
        }
        
        result = agent.analyze(sections)
        
        # 결과 검증
        assert result.agent_name == "OriginalityAgent"
        assert len(result.scores) > 0
        assert len(result.findings) > 0
        assert len(result.suggestions) > 0
        
        # 점수 범위 검증 (1-5)
        for score in result.scores.values():
            assert 1 <= score <= 5
        
        print(f"✅ OriginalityAgent 테스트 통과")
        print(f"   점수 개수: {len(result.scores)}")
        print(f"   발견사항: {len(result.findings)}")
        print(f"   제안사항: {len(result.suggestions)}")
    
    def test_lesson_extraction_agent(self):
        """교훈 추출 Agent 테스트"""
        agent = LessonExtractionAgent(self.guideline_manager)
        
        # 테스트용 섹션 (Conclusion만)
        sections = {
            "conclusion": self.sample_paper.conclusion
        }
        
        result = agent.analyze(sections)
        
        # 결과 검증
        assert result.agent_name == "LessonExtractionAgent"
        assert len(result.scores) > 0
        assert "교훈 명확성" in result.scores
        
        print(f"✅ LessonExtractionAgent 테스트 통과")
        print(f"   교훈 관련 점수: {result.scores.get('교훈 명확성', 0)}")
    
    def test_guideline_manager(self):
        """가이드라인 매니저 테스트"""
        guidelines = self.guideline_manager.get_guidelines_for_agent("originality")
        
        assert "평가 기준" in guidelines
        assert "핵심 질문" in guidelines
        assert "점수 가이드" in guidelines
        
        print(f"✅ GuidelineManager 테스트 통과")
        print(f"   가이드라인 길이: {len(guidelines)} 문자")

def run_tests():
    """테스트 실행"""
    print("=== TreeLLM Agent 테스트 시작 ===\n")
    
    test_class = TestAgents()
    test_class.setup_method()
    
    try:
        test_class.test_originality_agent()
        test_class.test_lesson_extraction_agent()
        test_class.test_guideline_manager()
        
        print("\n🎉 모든 테스트 통과!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise

if __name__ == "__main__":
    run_tests()
