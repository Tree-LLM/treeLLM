# example_usage.py - 실사용 예시

import sys
import os
sys.path.append('src')

from src.core import PaperSections
from treellm_system import TreeLLMSystem
from utils.pdf_processor import PDFProcessor, RelatedPaperProcessor
from utils.llm_interface import LLMFactory, MockLLMInterface

def example_basic_analysis():
    """기본 논문 분석 예시"""
    print("=== 기본 논문 분석 예시 ===\n")
    
    # 1. 논문 섹션 데이터 준비
    paper = PaperSections(
        introduction="""
        본 연구는 대화형 AI 시스템에서 발생하는 편향성 문제를 해결하기 위한 
        새로운 접근법을 제시한다. 기존의 방법들이 단순히 데이터 필터링에 
        의존했다면, 우리는 모델 아키텍처 수준에서의 편향성 완화 기법을 제안한다.
        """,
        related_work="""
        편향성 완화에 관한 기존 연구들은 크게 세 가지 범주로 나뉜다:
        1) 데이터 전처리 기반 접근법 (Smith et al., 2021)
        2) 후처리 보정 기법 (Johnson et al., 2022)  
        3) 공정성 제약 조건 추가 (Lee et al., 2023)
        그러나 이들 모두 근본적 한계를 가지고 있다.
        """,
        method="""
        제안하는 BiasLess 아키텍처는 다음 세 가지 핵심 구성요소로 이루어진다:
        1) Fairness-Aware Attention Module
        2) Demographic Parity Regularizer  
        3) Counterfactual Data Augmentation
        이를 통해 학습 과정에서 자동으로 편향성을 탐지하고 보정한다.
        """,
        experiments="""
        5개 벤치마크 데이터셋(IMDb, Amazon, Yelp, Twitter, Reddit)에서 
        실험을 수행했다. BiasLess는 기존 BERT 대비 공정성 지표에서 
        23.4% 향상을 보였으며, 성능 저하는 2.1%에 불과했다.
        통계적 유의성: p < 0.001, 95% 신뢰구간
        """,
        discussion="""
        결과 분석에 따르면 Fairness-Aware Attention이 가장 큰 기여를 했다.
        흥미롭게도 작은 데이터셋에서도 효과적이었는데, 이는 메타학습 
        특성 때문으로 추정된다. 다만 계산 오버헤드가 15% 증가하는 한계가 있다.
        """,
        conclusion="""
        본 연구를 통해 아키텍처 수준의 편향성 완화가 효과적임을 입증했다.
        특히 세 가지 교훈을 얻었다: 1) Attention 메커니즘의 중요성, 
        2) 정규화의 효과, 3) 데이터 증강의 한계. 이는 공정성과 성능의 
        균형점을 찾는 데 중요한 통찰을 제공한다.
        """
    )
    
    # 2. TreeLLM 시스템 초기화
    treellm = TreeLLMSystem()
    
    # 3. 토큰 사용량 미리 확인
    token_usage = treellm.get_agent_token_usage()
    print("Agent별 예상 토큰 사용량:")
    for agent, tokens in token_usage.items():
        print(f"  {agent}: ~{tokens:,} 토큰")
    
    total_tokens = sum(token_usage.values())
    print(f"  총 예상 토큰: ~{total_tokens:,} 토큰")
    print(f"  예상 비용: ~${total_tokens * 0.00003:.2f} (GPT-4 기준)\n")
    
    # 4. 논문 분석 실행
    print("분석 시작...")
    results = treellm.analyze_paper(
        paper_sections=paper,
        selected_agents=["OriginalityAgent", "LessonExtractionAgent"]
    )
    
    # 5. 결과 출력
    print("\n=== 📊 분석 결과 ===")
    summary = results['integrated_summary']
    print(f"전체 점수: {summary['overall_score']:.2f}/5.0")
    print(f"총 개선 제안: {summary['total_suggestions']}개")
    print(f"우선 개선사항: {', '.join(summary['priority_improvements'])}")
    
    # 6. Agent별 상세 결과
    print("\n=== 🤖 Agent별 상세 분석 ===")
    for agent_name, result in results['usenix_analysis'].items():
        print(f"\n[{agent_name}]")
        print("점수:")
        for criterion, score in result.scores.items():
            stars = "⭐" * int(score)
            print(f"  {criterion}: {score:.1f}/5.0 {stars}")
        
        print("주요 발견사항:")
        for finding in result.findings[:2]:
            print(f"  • {finding}")
        
        print("개선 제안:")
        for suggestion in result.suggestions[:2]:
            print(f"  💡 {suggestion}")
    
    return results

def example_pdf_analysis():
    """PDF 파일 분석 예시"""
    print("\n=== PDF 파일 분석 예시 ===\n")
    
    # 예시 PDF 파일 경로 (실제 파일이 있다면)
    pdf_path = "sample_paper.pdf"
    
    if os.path.exists(pdf_path):
        # PDF에서 섹션 추출
        sections_dict = PDFProcessor.extract_sections_from_pdf(pdf_path)
        
        # PaperSections 객체로 변환
        paper = PaperSections(**sections_dict)
        
        # 메타데이터 추출
        metadata = PDFProcessor.extract_metadata_from_pdf(pdf_path)
        print(f"논문 제목: {metadata.get('title', 'Unknown')}")
        print(f"페이지 수: {metadata.get('page_count', 0)}")
        
        # 분석 실행
        treellm = TreeLLMSystem()
        results = treellm.analyze_paper(paper_sections=paper)
        
        print(f"✅ PDF 분석 완료: {pdf_path}")
        
    else:
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        print("실제 PDF 파일을 준비하고 경로를 수정해주세요.")

def example_with_related_papers():
    """관련 논문과 함께 분석하는 예시"""
    print("\n=== 관련 논문 비교 분석 예시 ===\n")
    
    # 메인 논문
    paper = PaperSections(
        introduction="AI 편향성 문제 해결을 위한 연구...",
        related_work="기존 연구 Smith et al., Johnson et al. 검토...",
        method="BiasLess 아키텍처 제안...",
        experiments="5개 데이터셋에서 실험...",
        conclusion="아키텍처 수준 편향성 완화 효과적..."
    )
    
    # 관련 논문들 (실제로는 PDF에서 추출)
    related_papers = [
        {
            "title": "Fairness in Natural Language Processing",
            "authors": ["Smith, J.", "Brown, A."],
            "year": 2021,
            "abstract": "We propose a data preprocessing approach to mitigate bias...",
            "method": "Statistical parity constraint on training data",
            "contributions": ["Novel preprocessing pipeline", "Benchmark evaluation"]
        },
        {
            "title": "Post-processing Bias Correction for Language Models", 
            "authors": ["Johnson, M.", "Davis, R."],
            "year": 2022,
            "abstract": "A post-processing method to correct biased outputs...",
            "method": "Output calibration using demographic statistics",
            "contributions": ["Calibration algorithm", "Efficiency improvements"]
        },
        {
            "title": "Architectural Approaches to AI Fairness",
            "authors": ["Lee, S.", "Wilson, K."],
            "year": 2023,
            "abstract": "We integrate fairness constraints into model architecture...",
            "method": "Fairness-aware neural network design",
            "contributions": ["Novel architecture", "Theoretical analysis"]
        }
    ]
    
    # 분석 실행
    treellm = TreeLLMSystem()
    results = treellm.analyze_paper(
        paper_sections=paper,
        uploaded_papers=related_papers,
        selected_agents=["OriginalityAgent", "LessonExtractionAgent"]
    )
    
    # 비교 분석 결과 출력
    if results['comparison_analysis']:
        comp_result = results['comparison_analysis']
        print("=== 📚 관련 논문 비교 결과 ===")
        print("점수:")
        for criterion, score in comp_result.scores.items():
            print(f"  {criterion}: {score:.1f}/5.0")
        
        print("\n주요 발견사항:")
        for finding in comp_result.findings:
            print(f"  • {finding}")
        
        print("\n개선 제안:")
        for suggestion in comp_result.suggestions:
            print(f"  💡 {suggestion}")

def example_custom_agent():
    """커스텀 Agent 추가 예시"""
    print("\n=== 커스텀 Agent 추가 예시 ===\n")
    
    from src.agents.base_agent import BaseAgent
    from src.core import AgentResult, GuidelineManager
    
    class NoveltyAgent(BaseAgent):
        """참신성 평가 전용 Agent"""
        
        def __init__(self, guideline_manager: GuidelineManager):
            super().__init__("NoveltyAgent", guideline_manager)
        
        def analyze(self, sections):
            # 실제로는 LLM 호출하여 참신성 분석
            mock_result = {
                "scores": {
                    "기술적 참신성": 4.5,
                    "접근법 독창성": 4.2,
                    "아이디어 혁신성": 3.9
                },
                "findings": [
                    "아키텍처 수준 접근법이 매우 참신함",
                    "기존 연구와 차별화된 관점 제시",
                    "실용적 가치와 학술적 기여 균형"
                ],
                "suggestions": [
                    "참신성의 이론적 근거 보강",
                    "혁신적 요소의 명확한 설명",
                    "기존 방법과의 비교 강화"
                ]
            }
            
            return AgentResult(
                agent_name=self.name,
                scores=mock_result["scores"],
                findings=mock_result["findings"],
                suggestions=mock_result["suggestions"],
                analysis_details=mock_result
            )
    
    # 커스텀 Agent 테스트
    guideline_manager = GuidelineManager()
    novelty_agent = NoveltyAgent(guideline_manager)
    
    test_sections = {
        "introduction": "AI 편향성 문제를 아키텍처 수준에서 해결...",
        "method": "BiasLess 아키텍처 제안..."
    }
    
    result = novelty_agent.analyze(test_sections)
    
    print(f"✅ {result.agent_name} 분석 완료")
    print("참신성 점수:")
    for criterion, score in result.scores.items():
        print(f"  {criterion}: {score:.1f}/5.0")

def example_batch_analysis():
    """여러 논문 일괄 분석 예시"""
    print("\n=== 여러 논문 일괄 분석 예시 ===\n")
    
    # 여러 논문 데이터
    papers = [
        {
            "title": "AI Bias Mitigation Study",
            "sections": PaperSections(
                introduction="AI 편향성 완화 연구...",
                method="BiasLess 아키텍처...",
                conclusion="아키텍처 수준 접근법 효과적..."
            )
        },
        {
            "title": "Fairness in NLP Systems", 
            "sections": PaperSections(
                introduction="NLP 시스템의 공정성...",
                method="데이터 전처리 기법...",
                conclusion="전처리 방법의 한계..."
            )
        },
        {
            "title": "Ethical AI Development",
            "sections": PaperSections(
                introduction="윤리적 AI 개발...",
                method="윤리 제약 조건 통합...",
                conclusion="통합적 접근법 필요..."
            )
        }
    ]
    
    treellm = TreeLLMSystem()
    batch_results = []
    
    for paper_info in papers:
        print(f"분석 중: {paper_info['title']}")
        
        result = treellm.analyze_paper(
            paper_sections=paper_info['sections'],
            selected_agents=["OriginalityAgent"]
        )
        
        batch_results.append({
            "title": paper_info['title'],
            "overall_score": result['integrated_summary']['overall_score'],
            "results": result
        })
    
    # 일괄 결과 비교
    print("\n=== 📊 일괄 분석 결과 비교 ===")
    sorted_results = sorted(batch_results, key=lambda x: x['overall_score'], reverse=True)
    
    for i, paper_result in enumerate(sorted_results, 1):
        score = paper_result['overall_score']
        title = paper_result['title']
        print(f"{i}. {title}: {score:.2f}/5.0")

def main():
    """메인 실행 함수"""
    print("🌳 TreeLLM 시스템 사용 예시")
    print("=" * 50)
    
    try:
        # 1. 기본 분석
        results1 = example_basic_analysis()
        
        # 2. PDF 분석 (파일이 있을 경우)
        example_pdf_analysis()
        
        # 3. 관련 논문과 비교 분석
        example_with_related_papers()
        
        # 4. 커스텀 Agent 예시
        example_custom_agent()
        
        # 5. 일괄 분석
        example_batch_analysis()
        
        print("\n🎉 모든 예시 실행 완료!")
        print("\n다음 단계:")
        print("1. LLM API 키 설정 (OpenAI 또는 Anthropic)")
        print("2. 실제 PDF 파일로 테스트")
        print("3. 웹 인터페이스 구축")
        print("4. 추가 Agent 개발")
        
    except Exception as e:
        print(f"\n❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
