# treellm_system.py - 메인 시스템

from typing import Dict, List, Optional
from src.core import PaperSections, GuidelineManager, SectionExtractor
from src.agents import OriginalityAgent, LessonExtractionAgent, AssumptionAgent, RelatedPaperComparisonAgent

class TreeLLMSystem:
    """TreeLLM 메인 시스템"""
    
    def __init__(self):
        self.guideline_manager = GuidelineManager()
        self.section_extractor = SectionExtractor()
        
        # USENIX 전용 Agent들 (내장형)
        self.usenix_agents = {
            "OriginalityAgent": OriginalityAgent(self.guideline_manager),
            "LessonExtractionAgent": LessonExtractionAgent(self.guideline_manager),
            "AssumptionAgent": AssumptionAgent(self.guideline_manager)
        }
        
        # 관련 논문 비교 Agent (업로드형)
        self.comparison_agent = RelatedPaperComparisonAgent()
    
    def analyze_paper(self, 
                     paper_sections: PaperSections,
                     uploaded_papers: Optional[List[Dict]] = None,
                     selected_agents: Optional[List[str]] = None) -> Dict:
        """논문 전체 분석"""
        
        results = {
            "usenix_analysis": {},
            "comparison_analysis": None,
            "integrated_summary": {}
        }
        
        # USENIX Agent 분석
        agents_to_run = selected_agents or list(self.usenix_agents.keys())
        
        for agent_name in agents_to_run:
            if agent_name in self.usenix_agents:
                agent = self.usenix_agents[agent_name]
                
                # Agent별 필요 섹션 추출
                required_sections = self.section_extractor.extract_sections_for_agent(
                    paper_sections, agent_name
                )
                
                # Agent 실행
                result = agent.analyze(required_sections)
                results["usenix_analysis"][agent_name] = result
                
                print(f"✅ {agent_name} 분석 완료")
        
        # 관련 논문 비교 (업로드된 경우만)
        if uploaded_papers:
            comparison_result = self.comparison_agent.analyze(paper_sections, uploaded_papers)
            results["comparison_analysis"] = comparison_result
            print("✅ 관련논문 비교 분석 완료")
        
        # 결과 통합
        results["integrated_summary"] = self._integrate_results(results)
        
        return results
    
    def _integrate_results(self, results: Dict) -> Dict:
        """분석 결과 통합"""
        all_scores = {}
        all_suggestions = []
        priority_improvements = []
        
        # USENIX 분석 결과 통합
        for agent_name, result in results["usenix_analysis"].items():
            all_scores.update({f"{agent_name}_{k}": v for k, v in result.scores.items()})
            all_suggestions.extend(result.suggestions)
        
        # 비교 분석 결과 통합
        if results["comparison_analysis"]:
            comp_result = results["comparison_analysis"]
            all_scores.update({f"Comparison_{k}": v for k, v in comp_result.scores.items()})
            all_suggestions.extend(comp_result.suggestions)
        
        # 우선순위 개선사항 도출
        low_score_items = [(k, v) for k, v in all_scores.items() if v < 3.5]
        priority_improvements = [item[0] for item in sorted(low_score_items, key=lambda x: x[1])[:3]]
        
        return {
            "overall_score": sum(all_scores.values()) / len(all_scores) if all_scores else 0,
            "total_suggestions": len(all_suggestions),
            "priority_improvements": priority_improvements,
            "score_distribution": all_scores
        }
    
    def get_agent_token_usage(self) -> Dict[str, int]:
        """Agent별 예상 토큰 사용량 계산"""
        section_tokens = {
            "introduction": 1500,
            "related_work": 2000,
            "method": 2500, 
            "experiments": 3000,
            "discussion": 1500,
            "conclusion": 1000
        }
        
        usage = {}
        for agent_name in self.usenix_agents.keys():
            mapping = self.section_extractor.AGENT_SECTION_MAPPING.get(agent_name, "전체")
            
            if mapping == "전체":
                tokens = sum(section_tokens.values())
            else:
                section_names = ["introduction", "related_work", "method", 
                               "experiments", "discussion", "conclusion"]
                tokens = sum(section_tokens[section_names[i-1]] for i in mapping)
            
            usage[agent_name] = tokens
        
        return usage

# 사용 예시
def main():
    """TreeLLM 시스템 사용 예시"""
    
    # 논문 섹션 데이터 준비
    paper = PaperSections(
        introduction="본 연구는 자연어 처리에서 중요한 문제인...",
        related_work="기존 연구들은 다음과 같은 접근을 시도했다...",
        method="제안하는 방법은 Transformer 기반으로...",
        experiments="실험은 3개 데이터셋에서 수행되었다...",
        discussion="결과 분석에 따르면...",
        conclusion="결론적으로 본 연구는..."
    )
    
    # 업로드된 관련 논문 정보 (선택사항)
    uploaded_papers = [
        {"title": "Attention Is All You Need", "year": 2017, "authors": ["Vaswani et al."]},
        {"title": "BERT: Pre-training Transformers", "year": 2018, "authors": ["Devlin et al."]}
    ]
    
    # TreeLLM 시스템 초기화
    treellm = TreeLLMSystem()
    
    # 토큰 사용량 확인
    token_usage = treellm.get_agent_token_usage()
    print("Agent별 예상 토큰 사용량:")
    for agent, tokens in token_usage.items():
        print(f"  {agent}: ~{tokens} 토큰")
    
    # 논문 분석 실행
    results = treellm.analyze_paper(
        paper_sections=paper,
        uploaded_papers=uploaded_papers,
        selected_agents=["OriginalityAgent", "LessonExtractionAgent"]
    )
    
    # 결과 출력
    print("\n=== 분석 결과 ===")
    print(f"전체 점수: {results['integrated_summary']['overall_score']:.2f}")
    print(f"개선 제안 수: {results['integrated_summary']['total_suggestions']}")
    print("우선 개선사항:", results['integrated_summary']['priority_improvements'])
    
    return results

if __name__ == "__main__":
    results = main()
