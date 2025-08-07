# 🌳 TreeLLM V3.0 - AI 학술 논문 분석 파이프라인

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 소개

TreeLLM은 GPT-4와 같은 대규모 언어 모델을 활용하여 학술 논문을 7단계 파이프라인으로 자동 분석하고 구조화하는 AI 시스템입니다.

## ✨ 주요 기능

- **7단계 최적화 파이프라인**: Split → Build → Fuse → Audit → EditPass1 → GlobalCheck → EditPass2
- **4가지 프리셋**: Fast(빠른처리), Balanced(균형), Precision(정밀), Research(연구용)
- **지능형 캐싱**: 동일 문서 재처리 시 비용 없음
- **실시간 품질 메트릭**: 정확도, 완성도, 일관성 추적
- **웹 인터페이스**: 드래그앤드롭, 실시간 진행 표시
- **한국어/영어 지원**: 자동 언어 감지

## 🚀 빠른 시작

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/TreeLLM.git
cd TreeLLM

# 2. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate    # Windows

# 3. 패키지 설치
pip install -r requirements.txt

# 4. API 키 설정
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 사용법

```bash
# 🌐 웹 인터페이스 (추천)
python treellm.py --web

# 📄 파일 처리
python treellm.py sample/paper.txt --preset fast

# 🧪 시스템 테스트
python treellm.py --test

# 📝 샘플 생성
python treellm.py --create-sample
```

## 💰 비용 관리

| 프리셋 | 모델 | 1000단어 비용 | 속도 | 품질 |
|--------|------|---------------|------|------|
| Fast | GPT-3.5 | ~$0.02 | 2-3분 | ⭐⭐⭐ |
| Balanced | GPT-4o | ~$0.10 | 5-7분 | ⭐⭐⭐⭐ |
| Precision | GPT-4o | ~$0.12 | 10-12분 | ⭐⭐⭐⭐⭐ |
| Research | GPT-4o | ~$0.15 | 15-20분 | ⭐⭐⭐⭐⭐ |

💡 **팁**: 같은 문서를 재처리하면 캐시를 사용하여 **비용이 없습니다**!

## 📂 프로젝트 구조

```
TreeLLM/
├── treellm.py          # 🎯 메인 실행 파일
├── app.py              # 🌐 웹 인터페이스
├── Orchestrator.py     # 🔧 핵심 파이프라인
├── config.py           # ⚙️ 설정 파일
├── module/             # 📦 7단계 처리 모듈
├── prompts/            # 📝 GPT 프롬프트
├── sample/             # 📄 샘플 파일
├── results/            # 📊 분석 결과
├── cache/              # 💾 캐시 데이터
└── templates/          # 🎨 웹 템플릿
```

## 🧪 테스트

```bash
# 시스템 테스트 (API 호출 없음)
python test_system.py

# 한국어 안전 테스트
python safe_test_korean.py

# 하이퍼파라미터 테스트
python hyperparameter_testing.py --test-type quick
```

## 📊 출력 예시

```json
{
  "quality_metrics": {
    "overall_score": 0.85,
    "accuracy": 0.90,
    "completeness": 0.82,
    "consistency": 0.83
  },
  "performance": {
    "total_duration": 145.3,
    "total_tokens": 8432,
    "estimated_cost": 0.084
  }
}
```

## 🤝 기여

기여를 환영합니다! 이슈나 풀 리퀘스트를 자유롭게 제출해주세요.

## 📜 라이선스

MIT License

## 📞 문의

- 이슈: [GitHub Issues](https://github.com/yourusername/TreeLLM/issues)
- 이메일: your-email@example.com

---

Made with ❤️ by TreeLLM Team
