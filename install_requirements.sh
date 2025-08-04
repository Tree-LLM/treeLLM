#!/bin/bash
# TreeLLM 의존성 설치 스크립트

echo "TreeLLM 의존성 설치를 시작합니다..."

# 기본 패키지 설치
pip install flask flask-cors

# OpenAI 및 기타 필수 패키지
pip install openai python-dotenv

# 파일 처리 패키지
pip install PyMuPDF python-docx pypdf

# 데이터 처리 패키지
pip install pandas numpy tqdm

# 개발 도구 (선택사항)
# pip install pytest black flake8

echo "설치 완료!"
echo ""
echo "다음 명령어로 앱을 실행하세요:"
echo "export OPENAI_API_KEY='your-api-key-here'"
echo "python app_v2.py"