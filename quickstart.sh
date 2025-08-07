#!/bin/bash
# TreeLLM Quick Start Guide
# 빠른 시작을 위한 명령어 모음

echo "╔════════════════════════════════════════╗"
echo "║      🌳 TreeLLM V3.0 Quick Start       ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 색상 설정
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}1. 환경 설정${NC}"
echo "   source .venv/bin/activate"
echo "   export OPENAI_API_KEY='sk-your-key'"
echo ""

echo -e "${BLUE}2. 웹 인터페이스 실행${NC}"
echo "   python treellm.py --web"
echo "   # 브라우저: http://localhost:5001"
echo ""

echo -e "${YELLOW}3. CLI 실행 예시${NC}"
echo "   python treellm.py sample/paper.txt --preset fast"
echo "   python treellm.py sample/paper.txt --preset balanced"
echo ""

echo -e "${GREEN}4. 테스트${NC}"
echo "   python treellm.py --test              # 시스템 테스트"
echo "   python scripts/safe_test_korean.py    # 한국어 테스트"
echo ""

echo -e "${BLUE}5. 유용한 명령어${NC}"
echo "   python treellm.py --create-sample     # 샘플 생성"
echo "   python treellm.py --help              # 도움말"
echo "   ls results/                           # 결과 확인"
echo "   ls cache/                             # 캐시 확인"
echo ""

echo "────────────────────────────────────────"
echo "💡 팁: 같은 파일 재실행 시 캐시 사용 (무료)"
echo "💰 권장: fast 프리셋으로 시작 (최저 비용)"
echo "────────────────────────────────────────"
