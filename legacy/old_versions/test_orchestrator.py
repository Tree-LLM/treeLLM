#!/usr/bin/env python3
"""
TreeLLM 간단 테스트 스크립트
"""

from Orchestrator import OrchestratorV2
from config import load_config
import sys

def test_orchestrator():
    """Orchestrator 기본 테스트"""
    print("TreeLLM Orchestrator 테스트")
    print("=" * 50)
    
    # 설정 로드
    try:
        config = load_config("balanced")
        print("✓ 설정 로드 성공")
    except Exception as e:
        print(f"✗ 설정 로드 실패: {e}")
        return
    
    # Orchestrator 초기화
    try:
        orchestrator = OrchestratorV2(config)
        print("✓ Orchestrator 초기화 성공")
    except Exception as e:
        print(f"✗ Orchestrator 초기화 실패: {e}")
        return
    
    # 샘플 파일 확인
    sample_file = "sample/example.txt"
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ 샘플 파일 로드 성공 ({len(content)} 글자)")
    except Exception as e:
        print(f"✗ 샘플 파일 로드 실패: {e}")
        return
    
    print("\n테스트 완료! 이제 다음 명령으로 실행하세요:")
    print(f"python Orchestrator.py {sample_file}")

if __name__ == "__main__":
    test_orchestrator()
