# TreeLLM 프로젝트 구조

## 📁 핵심 파일
- `treellm.py` - 통합 메인 실행 파일
- `app.py` - Flask 웹 인터페이스
- `Orchestrator.py` - 7단계 파이프라인 핵심 로직
- `config.py` - 하이퍼파라미터 설정

## 📦 주요 디렉토리
- `module/` - 7단계 처리 모듈
  - split.py - 문서 분할
  - build.py - GPT 정보 추출
  - fuse.py - 트리 구조 생성
  - audit.py - 품질 검사
  - edit_pass1.py - 1차 편집
  - global_check.py - 전역 검사
  - edit_pass2.py - 최종 편집

- `prompts/` - GPT 프롬프트 템플릿
- `sample/` - 테스트용 샘플 파일
- `results/` - 분석 결과 저장
- `cache/` - 캐시 데이터 (재실행 시 비용 절감)
- `templates/` - 웹 UI HTML 템플릿
- `scripts/` - 테스트 및 유틸리티 스크립트

## 🔧 설정 파일
- `.env` - API 키 설정 (OPENAI_API_KEY)
- `requirements.txt` - Python 패키지 목록
- `quickstart.sh` - 빠른 시작 가이드

## 📚 문서
- `README.md` - 프로젝트 소개 및 사용법
- `API_DOCUMENTATION.md` - API 상세 문서
- `STRUCTURE.md` - 이 파일 (프로젝트 구조)

## 🗂️ 기타
- `backup/` - 백업 파일
- `legacy/` - 이전 버전 코드
- `v2/` - 버전 2 관련 파일
- `.git/` - Git 버전 관리
- `.venv/` - Python 가상환경
