#!/bin/bash

# run_treellm.sh - TreeLLM 실행 스크립트

echo "🌳 TreeLLM 시스템 시작"
echo "========================"

# 환경 변수 확인
if [ -f .env ]; then
    echo "✅ 환경 변수 파일 발견"
    source .env
else
    echo "⚠️  .env 파일이 없습니다. .env.example을 참고하여 생성하세요."
fi

# Python 경로 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# 실행 옵션 선택
echo ""
echo "실행할 모드를 선택하세요:"
echo "1) 웹 인터페이스 (Streamlit)"
echo "2) 예시 코드 실행"
echo "3) 테스트 실행"
echo "4) 커스텀 분석"

read -p "선택 (1-4): " choice

case $choice in
    1)
        echo "🌐 웹 인터페이스 시작..."
        streamlit run web_interface.py
        ;;
    2)
        echo "📝 예시 코드 실행..."
        python example_usage.py
        ;;
    3)
        echo "🧪 테스트 실행..."
        python tests/test_agents.py
        ;;
    4)
        echo "🔧 커스텀 분석 모드..."
        python -c "
from src.core import PaperSections
from treellm_system import TreeLLMSystem

print('커스텀 분석을 위한 Python 인터프리터가 시작됩니다.')
print('사용 예시:')
print('paper = PaperSections(introduction=\"본 연구는...\", method=\"제안하는 방법은...\")')
print('treellm = TreeLLMSystem()')  
print('results = treellm.analyze_paper(paper_sections=paper)')
print('')
"
        python
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "🎉 TreeLLM 실행 완료!"
