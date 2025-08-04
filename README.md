# TreeLLM - AI 논문 분석 파이프라인

TreeLLM은 대규모 언어 모델(LLM)을 활용하여 학술 논문을 계층적으로 분석하고 재구성하는 파이프라인입니다.

## 🚀 주요 기능

- **7단계 파이프라인**: Split → Build → Fuse → Audit → EditPass1 → GlobalCheck → EditPass2
- **하이퍼파라미터 최적화**: 다양한 프리셋과 커스터마이징 지원
- **병렬 처리**: 효율적인 API 호출을 위한 배치 처리
- **실시간 스트리밍**: 진행 상황을 실시간으로 확인
- **웹 인터페이스**: 사용하기 쉬운 Flask 기반 웹 UI

## 📦 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/TreeLLM.git
cd TreeLLM

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# 또는
.venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 OPENAI_API_KEY 설정
```

## 🔧 사용법

### 1. 웹 인터페이스

```bash
python app.py
```
브라우저에서 `http://localhost:5001` 접속

### 2. 커맨드 라인

```bash
# 기본 실행
python Orchestrator.py sample/example.txt

# 프리셋 사용
python Orchestrator.py sample/example.txt --preset research

# 커스텀 설정
python Orchestrator.py sample/example.txt --model gpt-4 --temperature 0.2
```

### 3. Python 코드

```python
from Orchestrator import OrchestratorV2
from config import load_config

# 프리셋 사용
orchestrator = OrchestratorV2(preset="balanced")
result = orchestrator.run("sample/example.txt")

# 커스텀 설정
config = load_config("balanced", 
    model={"temperature": 0.2, "max_tokens": 3072}
)
orchestrator = OrchestratorV2(config)
result = orchestrator.run("sample/example.txt")
```

## ⚙️ 설정 프리셋

- **fast**: 빠른 처리 (Temperature: 0.5, Workers: 5)
- **balanced**: 균형잡힌 처리 (Temperature: 0.3, Workers: 3) [기본값]
- **thorough**: 정밀한 분석 (Temperature: 0.2, Workers: 2)
- **research**: 연구용 최고 품질 (Temperature: 0.1, Workers: 2)

## 🧪 테스트

```bash
# 모듈 테스트
python tests/test_modules.py

# 하이퍼파라미터 튜닝
python tests/hyperparameter_tuning.py

# 기존 샘플로 효율적 테스트
python tests/efficient_hyperparameter_test.py
```

## 📂 프로젝트 구조

```
TreeLLM/
├── app.py                 # Flask 웹 애플리케이션
├── Orchestrator.py        # 메인 파이프라인 (v2)
├── config.py              # 설정 관리
├── module/                # 각 단계별 모듈
│   ├── split.py          # 문서 분할
│   ├── build.py          # GPT 프롬프트 실행
│   ├── fuse.py           # 트리 구조 생성
│   ├── audit.py          # 품질 검사
│   ├── edit_pass1.py     # 1차 편집
│   ├── global_check.py   # 전역 일관성 검사
│   └── edit_pass2.py     # 최종 편집
├── prompts/              # GPT 프롬프트 템플릿
├── sample/               # 샘플 데이터
├── tests/                # 테스트 스크립트
└── uploads/              # 업로드 파일 저장
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

기여를 환영합니다! 이슈나 풀 리퀘스트를 자유롭게 제출해주세요.
