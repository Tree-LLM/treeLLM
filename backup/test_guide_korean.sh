#!/bin/bash
# TreeLLM 한국어 테스트 스크립트
# 비용을 최소화하면서 단계별로 테스트합니다

echo "=================================================="
echo "TreeLLM V3 한국어 테스트 가이드"
echo "=================================================="
echo ""

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 경로 설정
cd /Users/kimminjun/Desktop/TreeLLM

echo -e "${GREEN}1. 환경 활성화${NC}"
echo "source /Users/kimminjun/Desktop/TreeLLM/.venv/bin/activate"
echo ""

echo -e "${GREEN}2. 무료 테스트 (API 호출 없음)${NC}"
echo "python safe_test_korean.py"
echo ""

echo -e "${GREEN}3. 작은 파일로 최소 비용 테스트 (약 $0.001)${NC}"
echo "python run_enhanced.py sample/tiny_korean_test.txt --preset fast"
echo ""

echo -e "${GREEN}4. 캐시 활용 테스트 (무료 - 3번 실행 후)${NC}"
echo "python run_enhanced.py sample/tiny_korean_test.txt --preset fast"
echo ""

echo -e "${YELLOW}5. 웹 인터페이스 실행${NC}"
echo "python app_v3.py"
echo "# 브라우저에서 http://localhost:5001 접속"
echo ""

echo -e "${GREEN}6. 결과 확인${NC}"
echo "ls -la results/"
echo "cat results/final_result_fast_*.json | python -m json.tool | head -30"
echo ""

echo "=================================================="
echo -e "${YELLOW}주의사항:${NC}"
echo "- fast 프리셋 사용 (GPT-3.5-turbo, 가장 저렴)"
echo "- 같은 파일 재실행 시 캐시 사용 (무료)"
echo "- --no-cache 옵션 사용하지 마세요"
echo "=================================================="
