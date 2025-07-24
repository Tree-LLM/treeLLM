# 🌳 TreeLLM: AI Agent 기반 논문 분석 시스템

**TreeLLM**은 USENIX Guidelines를 기반으로 한 AI Agent 시스템을 통해 학술 논문을 자동 분석하고 개선 제안을 제공하는 도구입니다.

## ✨ 주요 기능

### 🤖 **Agent 기반 전문 분석**
- **OriginalityAgent**: USENIX Original Ideas 기준으로 독창성 평가
- **LessonExtractionAgent**: USENIX Lessons 기준으로 교훈 추출 분석  
- **AssumptionAgent**: Method & Experiments의 가정사항 검증
- **RelatedPaperComparisonAgent**: 업로드한 관련 논문과 비교 분석

### 📋 **USENIX Guidelines 준수**
- **Original Ideas**: 문제 정의, 기존 기술 한계, 아이디어 중요성, 차별성
- **Reality**: 실제 구현 여부, 구현 완성도, 실용적 중요성
- **Lessons**: 교훈 명확성, 일반적 적용가능성, 전제 조건 명시

### 📄 **다양한 입력 방식**
- 텍스트 직접 입력
- PDF 파일 자동 섹션 추출
- 관련 논문 PDF 업로드를 통한 비교 분석

### 🎯 **정확한 섹션별 분석**
- Agent별 필요 섹션만 선별 입력 (토큰 효율성)
- Introduction + Related Work → OriginalityAgent
- Method + Experiments → AssumptionAgent  
- Conclusion → LessonExtractionAgent

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 저장소 클론
git clone https://github.com/treellm/treellm.git
cd TreeLLM

# 의존성 설치
pip install -r requirements.txt

# LLM API 키 설정
export OPENAI_API_KEY="your-openai-api-key"
# 또는
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 2. 기본 사용법
```python
from src.core import PaperSections
from treellm_system import TreeLLMSystem

# 논문 섹션 데이터 준비
paper = PaperSections(
    introduction="본 연구는...",
    related_work="기존 연구들은...",
    method="제안하는 방법은...",
    experiments="실험 결과...",
    conclusion="결론적으로..."
)

# TreeLLM 시스템 초기화 및 분석
treellm = TreeLLMSystem()
results = treellm.analyze_paper(
    paper_sections=paper,
    selected_agents=["OriginalityAgent", "LessonExtractionAgent"]
)

# 결과 확인
print(f"전체 점수: {results['integrated_summary']['overall_score']:.2f}/5.0")
```

### 3. 웹 인터페이스 실행
```bash
# Streamlit 웹 앱 실행
streamlit run web_interface.py
```

### 4. 예시 코드 실행
```bash
# 다양한 사용 예시 확인
python example_usage.py
```

## 📁 프로젝트 구조

```
TreeLLM/
├── src/                        # 메인 소스 코드
│   ├── core/                   # 핵심 모듈
│   │   ├── data_models.py      # 데이터 클래스
│   │   ├── guideline_manager.py # USENIX 가이드라인 관리
│   │   └── section_extractor.py # Agent별 섹션 매핑
│   └── agents/                 # Agent 모듈
│       ├── base_agent.py       # 기본 Agent 클래스
│       ├── usenix_agents.py    # USENIX 전용 Agent들
│       └── comparison_agents.py # 관련논문 비교 Agent
├── utils/                      # 유틸리티
│   ├── pdf_processor.py        # PDF 처리
│   └── llm_interface.py        # LLM API 인터페이스  
├── tests/                      # 테스트
│   └── test_agents.py          # Agent 테스트
├── treellm_system.py          # 메인 시스템
├── example_usage.py           # 사용 예시
├── web_interface.py           # Streamlit 웹 인터페이스
├── requirements.txt           # 의존성
└── setup.py                   # 패키지 설정
```

## 🔧 Agent별 분석 범위

| Agent | 입력 섹션 | 분석 내용 | USENIX 기준 |
|-------|-----------|-----------|-------------|
| **OriginalityAgent** | Introduction + Related Work | 독창성, 차별점, 문제 정의 | Original Ideas |  
| **LessonExtractionAgent** | Conclusion | 교훈 추출, 일반화 가능성 | Lessons |
| **AssumptionAgent** | Method + Experiments | 가정사항, 전제 조건 | - |
| **RelatedPaperComparisonAgent** | 전체 + 업로드 논문 | 관련연구 비교, 포지셔닝 | - |

## 💡 사용 예시

### 기본 분석
```python
# 간단한 논문 분석
results = treellm.analyze_paper(paper_sections=paper)
```

### 관련 논문과 비교 분석
```python
# 관련 논문 정보 준비
related_papers = [
    {"title": "Related Work 1", "year": 2023, "authors": ["Smith et al."]},
    {"title": "Related Work 2", "year": 2022, "authors": ["Johnson et al."]}
]

# 비교 분석 실행
results = treellm.analyze_paper(
    paper_sections=paper,
    uploaded_papers=related_papers
)
```

### PDF 파일 분석
```python
from utils.pdf_processor import PDFProcessor

# PDF에서 섹션 자동 추출
sections_dict = PDFProcessor.extract_sections_from_pdf("paper.pdf")
paper = PaperSections(**sections_dict)

# 분석 실행
results = treellm.analyze_paper(paper_sections=paper)
```

## 📊 결과 형식

```json
{
  "usenix_analysis": {
    "OriginalityAgent": {
      "scores": {
        "문제 정의 명확성": 4.2,
        "기존 기술 한계 설명": 3.8,
        "아이디어 중요성": 4.0,
        "기존 연구와 차별성": 3.5
      },
      "findings": ["발견사항1", "발견사항2"],
      "suggestions": ["개선제안1", "개선제안2"]
    }
  },
  "integrated_summary": {
    "overall_score": 3.95,
    "total_suggestions": 8,
    "priority_improvements": ["우선개선1", "우선개선2"]
  }
}
```

## 🧪 테스트

```bash
# Agent 테스트 실행
python tests/test_agents.py

# 또는 pytest 사용
pytest tests/
```

## 🔗 LLM 제공자 지원

- **OpenAI GPT-4/GPT-3.5**: `LLMFactory.create_llm("openai")`
- **Anthropic Claude**: `LLMFactory.create_llm("anthropic")`  
- **Mock LLM**: 테스트용 `MockLLMInterface()`

## 📈 토큰 사용량 최적화

```python
# Agent별 토큰 사용량 확인
token_usage = treellm.get_agent_token_usage()
print(token_usage)

# 출력 예시:
# {
#   'OriginalityAgent': 3500,      # Introduction + Related Work
#   'LessonExtractionAgent': 1000, # Conclusion만
#   'AssumptionAgent': 5500        # Method + Experiments
# }
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👥 개발팀

- **TreeLLM Team** - 초기 개발 및 유지보수

## 🔖 버전 히스토리

- **v0.1.0** - 초기 릴리즈
  - USENIX Guidelines 기반 Agent 시스템
  - PDF 자동 처리
  - 웹 인터페이스
  - 관련 논문 비교 기능

## 📞 지원

문제가 발생하거나 질문이 있으시면 [Issues](https://github.com/treellm/treellm/issues)에 등록해 주세요.

---

**TreeLLM으로 더 나은 논문을 작성하세요! 🚀**
