#!/usr/bin/env python3
"""
TreeLLM 안전한 한국어 테스트 스크립트
비용을 최소화하면서 시스템을 테스트합니다.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# 환경 설정
os.chdir('/Users/kimminjun/Desktop/TreeLLM')
sys.path.insert(0, '/Users/kimminjun/Desktop/TreeLLM')

def test_without_api():
    """API 호출 없이 테스트"""
    print("="*60)
    print("🔧 TreeLLM 무료 테스트 (API 호출 없음)")
    print("="*60)
    
    # 1. 모듈 임포트 테스트
    print("\n1️⃣ 모듈 임포트 테스트...")
    try:
        from Orchestrator import EnhancedOrchestratorV3
        print("✅ Orchestrator_v3 임포트 성공")
        
        # 프리셋 확인
        print("\n사용 가능한 프리셋:")
        for preset_name, preset_info in EnhancedOrchestratorV3.PRESETS.items():
            print(f"  - {preset_name}: {preset_info['description']}")
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False
    
    # 2. 샘플 파일 확인
    print("\n2️⃣ 샘플 파일 확인...")
    sample_dir = Path("sample")
    
    # 작은 테스트 파일 찾기
    test_files = [
        "tiny_korean_test.txt",
        "minimal.txt", 
        "tiny.txt"
    ]
    
    found_file = None
    for test_file in test_files:
        file_path = sample_dir / test_file
        if file_path.exists():
            found_file = file_path
            file_size = len(file_path.read_text(encoding='utf-8'))
            print(f"✅ 테스트 파일: {test_file} ({file_size} 글자)")
            break
    
    if not found_file:
        print("⚠️ 작은 테스트 파일이 없습니다. 생성합니다...")
        found_file = sample_dir / "tiny_korean_test.txt"
        if found_file.exists():
            print(f"✅ 이미 생성됨: {found_file}")
    
    # 3. 캐시 확인
    print("\n3️⃣ 캐시 확인...")
    cache_dir = Path("sample/cache")
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.json"))
        print(f"✅ 캐시 파일 {len(cache_files)}개 발견")
        for cf in cache_files[:3]:
            print(f"  - {cf.name}")
    else:
        print("⚠️ 캐시 디렉토리 없음")
    
    # 4. 비용 예측
    if found_file and found_file.exists():
        print("\n4️⃣ 비용 예측...")
        content = found_file.read_text(encoding='utf-8')
        words = len(content.split())
        tokens = words * 1.3  # 대략적인 토큰 변환
        
        print(f"📄 파일: {found_file.name}")
        print(f"📝 단어 수: {words}")
        print(f"🎯 예상 토큰: {int(tokens)}")
        print(f"\n💰 프리셋별 예상 비용:")
        print(f"  fast (GPT-3.5): ${tokens/1000 * 0.002 * 7:.4f}")
        print(f"  balanced (GPT-4o): ${tokens/1000 * 0.01 * 7:.4f}")
        print(f"  precision (GPT-4o): ${tokens/1000 * 0.01 * 7 * 1.2:.4f}")
        print(f"  research (GPT-4o): ${tokens/1000 * 0.01 * 7 * 1.5:.4f}")
    
    print("\n" + "="*60)
    print("✅ 무료 테스트 완료!")
    print("="*60)
    
    return True

def test_split_only():
    """Split 모듈만 테스트 (API 호출 없음)"""
    print("\n" + "="*60)
    print("🔍 Split 모듈 테스트 (API 호출 없음)")
    print("="*60)
    
    try:
        from module.split import run as split_run
        
        # 테스트 텍스트
        test_text = """
# 제목
## 소개
이것은 테스트입니다.
## 방법론
테스트 방법입니다.
## 결론
테스트 완료.
"""
        
        result = split_run(test_text)
        print(f"✅ Split 결과: {len(result)}개 섹션")
        for section_name in result.keys():
            print(f"  - {section_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Split 테스트 실패: {e}")
        return False

def check_api_key():
    """API 키 확인"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        if api_key.startswith('sk-'):
            print("✅ OpenAI API 키 설정됨")
            return True
        else:
            print("⚠️ API 키 형식이 올바르지 않을 수 있습니다")
            return False
    else:
        print("❌ API 키가 설정되지 않았습니다")
        return False

def main():
    print("\n🚀 TreeLLM V3 한국어 테스트 시작\n")
    
    # 1. 무료 테스트
    test_without_api()
    
    # 2. Split 모듈 테스트
    test_split_only()
    
    # 3. API 키 확인
    print("\n" + "="*60)
    print("🔑 API 키 상태")
    print("="*60)
    has_key = check_api_key()
    
    if has_key:
        print("\n💡 실제 파이프라인 실행 명령:")
        print("  최소 비용: python run_enhanced.py sample/tiny_korean_test.txt --preset fast")
        print("  캐시 활용: 위 명령을 다시 실행하면 캐시 사용 (무료)")
    else:
        print("\n⚠️ API 키 없이는 실제 파이프라인을 실행할 수 없습니다")
        print("  .env 파일에 OPENAI_API_KEY를 설정하세요")
    
    print("\n✅ 테스트 완료!\n")

if __name__ == "__main__":
    main()
