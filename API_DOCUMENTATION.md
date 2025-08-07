# TreeLLM Extended API Documentation

## 개요

TreeLLM Extended API는 기존의 2개 엔드포인트에서 20개 이상의 세분화된 엔드포인트로 확장되었습니다. 이를 통해 더 세밀한 제어와 효율적인 처리가 가능합니다.

## Base URL
```
http://localhost:5001/api
```

## 인증
- Session ID를 통한 세션 관리: `X-Session-ID` 헤더

## 엔드포인트 목록

### 1. 시스템 관리
- `GET /api/health` - 서버 상태 확인
- `GET /api/cache` - 캐시 상태 조회
- `DELETE /api/cache` - 오래된 캐시 정리

### 2. 설정 관리
- `GET /api/presets` - 사용 가능한 프리셋 목록
- `GET /api/config` - 설정 조회
- `POST /api/config` - 커스텀 설정 생성
- `POST /api/estimate-cost` - 비용 예측

### 3. 파일 관리
- `POST /api/upload` - 파일 업로드
- `GET /api/files` - 업로드된 파일 목록

### 4. 개별 모듈 실행
- `POST /api/modules/split` - Split 모듈만 실행 (무료)
- `POST /api/modules/fuse` - Fuse 모듈만 실행 (무료)
- `POST /api/modules/test` - 모듈 테스트 (Mock 지원)

### 5. 파이프라인 실행
- `POST /api/pipeline/start` - 파이프라인 비동기 실행
- `GET /api/pipeline/status/{job_id}` - 실행 상태 조회
- `GET /api/pipeline/stream/{job_id}` - 실시간 상태 스트리밍 (SSE)
- `POST /api/pipeline/cancel/{job_id}` - 실행 취소

### 6. 결과 관리
- `GET /api/results/{job_id}` - 실행 결과 조회
- `GET /api/results/{job_id}/download` - 결과 다운로드 (JSON/Markdown)
- `GET /api/jobs` - 작업 목록 조회

## 주요 기능

### 1. 비동기 처리
```bash
# 파이프라인 시작
curl -X POST http://localhost:5001/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{
    "text": "논문 내용...",
    "preset": "balanced"
  }'

# 응답
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "started",
  "estimated_time": 60,
  "estimated_cost": 0.25
}
```

### 2. 실시간 진행 상황 확인 (SSE)
```javascript
const eventSource = new EventSource('/api/pipeline/stream/123e4567-e89b-12d3-a456-426614174000');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}%, Current step: ${data.current_step}`);
};
```

### 3. 개별 모듈 테스트
```bash
# Split 모듈만 실행 (API 키 불필요)
curl -X POST http://localhost:5001/api/modules/split \
  -H "Content-Type: application/json" \
  -d '{"text": "논문 내용..."}'

# Mock 모드로 테스트
curl -X POST http://localhost:5001/api/modules/test \
  -H "Content-Type: application/json" \
  -d '{
    "module": "audit",
    "mock": true
  }'
```

### 4. 비용 예측
```bash
curl -X POST http://localhost:5001/api/estimate-cost \
  -H "Content-Type: application/json" \
  -d '{
    "text_length": 10000,
    "preset": "balanced"
  }'

# 응답
{
  "preset": "balanced",
  "text_length": 10000,
  "costs_by_module": {
    "build": 0.21,
    "audit": 0.045,
    "edit1": 0.105,
    "global_check": 0.035,
    "edit2": 0.07
  },
  "total_cost": 0.465,
  "currency": "USD",
  "model": "gpt-4o"
}
```

### 5. 파일 업로드 및 처리
```bash
# 파일 업로드
curl -X POST http://localhost:5001/api/upload \
  -F "file=@paper.pdf"

# 업로드된 파일로 파이프라인 실행
curl -X POST http://localhost:5001/api/pipeline/start \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "uploaded-file-id",
    "preset": "thorough"
  }'
```

### 6. 결과 다운로드
```bash
# JSON 형식
curl http://localhost:5001/api/results/{job_id}/download?format=json -o result.json

# Markdown 형식
curl http://localhost:5001/api/results/{job_id}/download?format=markdown -o result.md
```

## 에러 처리

모든 에러는 다음 형식으로 반환됩니다:
```json
{
  "error": "에러 메시지"
}
```

HTTP 상태 코드:
- 200: 성공
- 400: 잘못된 요청
- 402: 결제 필요 (API 키 필요한 모듈)
- 404: 리소스를 찾을 수 없음
- 413: 파일 크기 초과
- 500: 서버 내부 오류

## 장점

1. **세밀한 제어**: 각 모듈을 개별적으로 실행 가능
2. **비용 효율성**: 필요한 모듈만 실행
3. **비동기 처리**: 긴 작업도 차단 없이 처리
4. **실시간 모니터링**: SSE를 통한 진행 상황 추적
5. **Mock 지원**: API 비용 없이 테스트 가능
6. **다양한 출력 형식**: JSON, Markdown 등
7. **세션 관리**: 여러 파일과 작업을 관리

## 사용 예시

### Python 클라이언트
```python
import requests
import json

# 서버 상태 확인
response = requests.get("http://localhost:5001/api/health")
print(response.json())

# 텍스트로 파이프라인 실행
data = {
    "text": "논문 내용...",
    "preset": "balanced"
}
response = requests.post("http://localhost:5001/api/pipeline/start", json=data)
job_info = response.json()

# 상태 확인
job_id = job_info["job_id"]
status = requests.get(f"http://localhost:5001/api/pipeline/status/{job_id}")
print(status.json())
```

### JavaScript/Frontend
```javascript
// 파일 업로드
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const { file } = await uploadResponse.json();

// 파이프라인 실행
const pipelineResponse = await fetch('/api/pipeline/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: file.id,
    preset: 'balanced'
  })
});

const { job_id } = await pipelineResponse.json();

// 실시간 진행 상황 모니터링
const eventSource = new EventSource(`/api/pipeline/stream/${job_id}`);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateProgressBar(data.progress);
};
```
