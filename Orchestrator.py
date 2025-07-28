"""
orchestrate.py
──────────────
전체 파이프라인을 한 번에 실행하는 Orchestrator 클래스 정의.
"""
from pathlib import Path
from openai import OpenAI
import treeLLM.module as M


class Orchestrator:
    """논문(텍스트) 파일 경로를 받아 모든 단계를 순차 실행합니다."""

    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    # ────────────────────────────────────────────
    # 내부 공용: OpenAI 호출 래퍼
    def _call(self, prompt: str) -> str:
        return (
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            .choices[0]
            .message.content
        )

    # ────────────────────────────────────────────
    def run(self, text_path: str):
        """`text_path`(md / txt) → 최종 수정본 문자열 반환"""
        raw_text = Path(text_path).read_text(encoding="utf-8")

        # 1. 섹션·문단 구분
        sections = M.split(raw_text)

        # 2. 문단 → 트리
        trees = [M.build(p.text, p.section, self._call) for p in sections]

        # 3. 트리 병합 (mode=0: 실제 병합, 1: 미리보기)
        full_tree = M.fuse(trees, mode=0, call_gpt=self._call)

        # 4. USENIX 검정
        audit_result = M.audit(full_tree, self._call)

        # 5. 1차 수정안 + 5-b 요약본
        a_file = M.edit_pass1(sections, audit_result, self._call)
        b_file = M.summarize(a_file, self._call)

        # 6. 전역 점검
        c_file = M.review(b_file, self._call)

        # 7. 2차 수정 적용
        updated_a = M.edit_pass2(a_file, c_file, self._call)

        # 8. 최종 결과 패키징
        final_output = M.finalize(updated_a, full_tree, audit_result)

        return final_output
