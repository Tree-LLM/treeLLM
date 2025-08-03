# TreeLLM - Advanced Paper Analysis System

논문 분석을 위한 고급 LLM 파이프라인 시스템

## 주요 특징

### 🚀 하이퍼파라미터 최적화
- **세밀한 파라미터 제어**: Temperature, Top-p, Max Tokens 등 모든 주요 파라미터 조정 가능
- **프리셋 시스템**: Fast, Balanced, Thorough, Research 프리셋 제공
- **모델별 최적화**: GPT-4o, GPT-4, GPT-3.5-turbo별 최적 설정
- **병렬 처리**: 멀티스레드를 활용한 빠른 처리

### 📊 고급 분석 기능
- **7단계 분석 파이프라인**
  1. Split - 문서 섹션 분할
  2. Build - LLM 프롬프트 실행
  3. Fuse - 트리 구조 생성
  4. Audit - 품질 감사
  5. Edit Pass 1 - 1차 편집
  6. Global Check - 전역 일관성 검사
  7. Edit Pass 2 - 최종 편집

### 🎯 지능형 기능
- **적응형 트리 구조**: 논문 구조에 맞춘 동적 트리 생성
- **품질 점수 시스템**: 각 단계별 품질 평가 및 피드백
- **실시간 스트리밍**: 분석 진행 상황 실시간 확인
- **다양한 파일 지원**: PDF, DOCX, TXT, Markdown

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/TreeLLM.git
cd TreeLLM
```

### 2. 가상환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 사용 방법

### 웹 인터페이스 (권장)
```bash
python app_v2.py
```
브라우저에서 `http://localhost:5001` 접속

### 커맨드 라인
```bash
# 기본 사용
python v2/OrchestratorV2.py sample/example.txt

# 프리셋 사용
python v2/OrchestratorV2.py sample/example.txt --preset research

# 커스텀 설정
python v2/OrchestratorV2.py sample/example.txt --temperature 0.2 --model gpt-4

# 스트리밍 모드
python v2/OrchestratorV2.py sample/example.txt --stream
```

## 설정 프리셋

### Fast (빠른 처리)
- Temperature: 0.5
- 병렬 처리: 5 workers
- 기본적인 분석에 적합

### Balanced (균형)
- Temperature: 0.3
- 병렬 처리: 3 workers
- 일반적인 논문 분석에 권장

### Thorough (정밀)
- Temperature: 0.2
- 병렬 처리: 2 workers
- 세밀한 분석이 필요한 경우

### Research (연구용)
- Temperature: 0.1
- 병렬 처리: 2 workers
- 최고 품질의 분석

## 하이퍼파라미터 설정

### config.py 구조
```python
config = TreeLLMConfig(
    model=ModelConfig(
        model_name="gpt-4o",
        temperature=0.3,
        top_p=0.3,
        max_tokens=4096
    ),
    build=BuildConfig(
        parallel_processing=True,
        max_workers=3,
        retry_attempts=3
    ),
    audit=AuditConfig(
        strictness_level="medium",
        detailed_feedback=True
    )
)
```

### 커스텀 설정 예시
```python
from config import load_config

# 프리셋 기반 커스터마이징
config = load_config(
    "thorough",
    model={"temperature": 0.15},
    debug_mode=True
)

orchestrator = OrchestratorV2(config)
```

## API 엔드포인트

### POST /api/analyze
논문 분석 실행 (동기)

### POST /api/analyze/stream
논문 분석 실행 (스트리밍)

### GET /api/presets
사용 가능한 프리셋 목록

### GET /api/config/{preset}
특정 프리셋의 상세 설정

### GET /api/status
시스템 상태 확인

## 프로젝트 구조
```
TreeLLM/
├── config.py              # 하이퍼파라미터 설정
├── v2/
│   └── OrchestratorV2.py  # 메인 파이프라인 (최적화 버전)
├── module/                # 각 단계별 모듈
│   ├── split.py          # 문서 분할
│   ├── build.py          # LLM 프롬프트 실행
│   ├── fuse.py           # 트리 구조 생성
│   ├── audit.py          # 품질 감사
│   ├── edit_pass1.py     # 1차 편집
│   ├── global_check.py   # 전역 검사
│   └── edit_pass2.py     # 최종 편집
├── prompts/              # 프롬프트 템플릿
├── app_v2.py            # Flask 웹 앱
└── templates/           # 웹 UI 템플릿
```

## 성능 최적화 팁

1. **병렬 처리 활용**
   - 여러 프롬프트를 동시에 실행하여 속도 향상
   - CPU 코어 수에 맞춰 max_workers 조정

2. **캐싱 활용**
   - 중간 결과 저장으로 재실행 시간 단축
   - save_intermediate_results 설정 활용

3. **적절한 프리셋 선택**
   - 논문 길이와 복잡도에 따라 적절한 프리셋 선택
   - 초기 테스트는 Fast 프리셋으로 시작

4. **메모리 관리**
   - 대용량 PDF 처리 시 충분한 메모리 확보
   - 필요시 섹션별 처리 고려

## 문제 해결

### API 키 오류
```bash
export OPENAI_API_KEY="sk-..."
```

### 메모리 부족
- max_section_length 파라미터 조정
- 병렬 처리 worker 수 감소

### 타임아웃 오류
- timeout 파라미터 증가
- retry_attempts 증가

## 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이센스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 문의

- Issue Tracker: [GitHub Issues](https://github.com/yourusername/TreeLLM/issues)
- Email: your.email@example.com
