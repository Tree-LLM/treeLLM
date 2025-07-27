# Tree-LLM: Structured Paper Tree Schema for LLM Analysis

This repository provides a tree-structured schema for analyzing academic papers using Large Language Models (LLMs).  
By decomposing each section of a paper (Abstract, Introduction, Method, etc.) into fine-grained nodes,  
this project aims to enable automatic parsing, logical consistency checking, and prompt-based rewriting for academic writing.

# 🧠 논문 구조 분석 및 수정 시스템 전체 흐름

이 시스템은 논문을 **문단 단위로 분석**하고,  
**논리 구조 트리 구축 → USENIX 기준 검정 → 문단 수정 제안 → 전역 흐름 점검**까지  
전 과정을 자동화한 구조 기반 학술 글쓰기 지원 파이프라인입니다.

---

## 🐵 사전 준비

### 1. 섹션 및 문단 구분
- 전체 논문 텍스트를 섹션 단위로 분할
- 각 문단에는 고유한 **섹션명 + 문단 번호** 부여  
  *(예: Introduction-1, 1-1 등)*

---

### 2. 트리 채우기 (Fill Prompt)
- **Input**: 각 문단 텍스트
- **Output**: 해당 문단에서 추출된 논리 구조 트리 노드  
  *(예: 문제 진술, 제안 방법, 연구 공백 등)*

---

### 3. 트리 병합 (Merge Prompt)
- **Input**: 한 섹션에 속한 여러 문단의 트리들
- **Output**: 섹션 단위 통합 트리 (`sectionX_tree.json`)
- 병합된 트리는 `.json` 형식으로 저장되어 사용자 다운로드 가능

---

## 🦊 검정 단계

### 4. USENIX 기준 검정
- **Input**: 섹션별 트리 + USENIX 기준
- **Output**: 각 항목(Originality, Gap, Assumption 등)에 대한 평가
- 모든 평가 결과를 `usenix_eval.json` 파일에 저장

---

## 🐰 수정 제안

### 5. 1차 수정 (문단 단위)
- **Input**: 각 문단 텍스트  
  → 해당 문단의 트리 및 USENIX 평가를 바탕으로 수정 제안 생성
- **Output**:  
  - `a_file`: 문단별 수정 제안  
  - `b_file`: 문단별 요약 리스트

---

### 6. 2차 수정 (전역 흐름 점검)
- **Input**: `b_file` (모든 문단 요약 리스트)
- 중복, 단절, 누락, 순서 문제 등 전역 흐름 이슈 점검
- **Output**:  
  - `c_file`: 섹션 단위 수정 방향 안내서

---

### 7. 최종 수정 업데이트
- **Input**:  
  - `c_file`: 수정 방향 안내  
  - `a_file`: 기존 문단별 수정 제안
- 해당 문단들을 다시 수정해 **최종본** 생성
- 결과는 `a_file`에 업데이트

---

### 8. 최종 수정 제안 반환
- 최종 수정 제안이 담긴 `a_file`을 사용자에게 반환
- 필요 시 `.md`, `.pdf`, `.json` 등 다양한 형식으로 다운로드 가능

---
