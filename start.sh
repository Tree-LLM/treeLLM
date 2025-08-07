#!/bin/bash
# TreeLLM 시작 스크립트

echo "TreeLLM - AI 논문 분석 파이프라인"
echo "================================"

# Python 버전 확인
python_version=$(python3 --version 2>&1)
echo "Python 버전: $python_version"

# 가상환경 확인
if [ -d ".venv" ]; then
    echo "가상환경을 활성화합니다..."
    source .venv/bin/activate
else
    echo "가상환경을 생성합니다..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "의존성을 설치합니다..."
    pip install -r requirements.txt
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo ".env 파일이 없습니다. .env.example을 복사합니다..."
        cp .env.example .env
        echo "⚠️  .env 파일에 OPENAI_API_KEY를 설정해주세요!"
        exit 1
    fi
fi

# API 키 확인
if grep -q "your-api-key-here" .env; then
    echo "⚠️  .env 파일에 실제 OPENAI_API_KEY를 설정해주세요!"
    exit 1
fi

# 메뉴 표시
echo ""
echo "실행 옵션을 선택하세요:"
echo "1) 웹 인터페이스 실행 (권장)"
echo "2) 커맨드 라인 실행"
echo "3) 테스트 실행"
echo "4) 하이퍼파라미터 튜닝"
echo "5) 종료"
echo ""
read -p "선택 (1-5): " choice

case $choice in
    1)
        echo "웹 인터페이스를 시작합니다..."
        echo "브라우저에서 http://localhost:5001 접속"
        python app.py
        ;;
    2)
        echo "샘플 파일로 실행합니다..."
        python Orchestrator.py sample/example.txt --preset balanced
        ;;
    3)
        echo "테스트를 실행합니다..."
        python tests/test_modules.py --config balanced
        ;;
    4)
        echo "하이퍼파라미터 튜닝을 시작합니다..."
        python tests/efficient_hyperparameter_test.py
        ;;
    5)
        echo "종료합니다."
        exit 0
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac
