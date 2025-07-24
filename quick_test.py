# quick_test.py - VSCode에서 빠른 테스트용

import sys
import os

# 경로 설정
sys.path.append('src')

print("🌳 TreeLLM 빠른 테스트")
print("=" * 30)

try:
    # 1. 모듈 임포트 테스트
    from src.core import PaperSections, GuidelineManager
    from treellm_system import TreeLLMSystem
    print("✅ 모듈 임포트 성공!")
    
    # 2. 간단한 논문 데이터
    paper = PaperSections(
        introduction="본 연구는 AI 편향성 문제를 해결하기 위한 새로운 접근법을 제시한다.",
        related_work="기존 연구들은 데이터 전처리나 후처리에 집중했으나 한계가 있다.",
        method="제안하는 BiasLess 아키텍처는 세 가지 핵심 구성요소로 이루어진다.",
        experiments="5개 벤치마크에서 실험한 결과 23.4% 성능 향상을 달성했다.",
        conclusion="아키텍처 수준의 편향성 완화가 효과적임을 입증했다."
    )
    print("✅ 논문 데이터 생성 성공!")
    
    # 3. TreeLLM 시스템 초기화
    treellm = TreeLLMSystem()
    print("✅ TreeLLM 시스템 초기화 성공!")
    
    # 4. 토큰 사용량 확인
    token_usage = treellm.get_agent_token_usage()
    print(f"✅ 토큰 사용량 계산 성공!")
    print("Agent별 예상 토큰:")
    for agent, tokens in token_usage.items():
        print(f"  - {agent}: {tokens:,} 토큰")
    
    # 5. Mock 모드로 분석 실행 (API 키 없이도 동작)
    print("\n🔄 Mock 모드로 분석 시작...")
    results = treellm.analyze_paper(
        paper_sections=paper,
        selected_agents=["OriginalityAgent", "LessonExtractionAgent"]
    )
    
    # 6. 결과 출력
    print("\n📊 분석 결과:")
    summary = results['integrated_summary']
    print(f"전체 점수: {summary['overall_score']:.2f}/5.0")
    print(f"총 개선 제안: {summary['total_suggestions']}개")
    print(f"우선 개선사항: {len(summary['priority_improvements'])}개")
    
    # 7. Agent별 상세 결과
    print("\n🤖 Agent별 분석:")
    for agent_name, result in results['usenix_analysis'].items():
        print(f"\n[{agent_name}]")
        avg_score = sum(result.scores.values()) / len(result.scores)
        print(f"  평균 점수: {avg_score:.1f}/5.0")
        print(f"  발견사항: {len(result.findings)}개")
        print(f"  개선 제안: {len(result.suggestions)}개")
    
    print("\n🎉 모든 테스트 성공! TreeLLM이 정상 동작합니다.")
    
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    print("💡 해결방법:")
    print("1. PYTHONPATH 설정: export PYTHONPATH=\"${PYTHONPATH}:$(pwd)/src\"")
    print("2. 터미널에서 TreeLLM 폴더에 있는지 확인")
    
except Exception as e:
    print(f"❌ 실행 중 오류: {e}")
    print("💡 에러 내용을 확인하고 문제를 해결해주세요.")

print("\n" + "=" * 50)
print("VSCode에서 TreeLLM 사용 방법:")
print("1. 터미널에서: python quick_test.py")
print("2. 웹 인터페이스: streamlit run web_interface.py")
print("3. 예시 코드: python example_usage.py")
