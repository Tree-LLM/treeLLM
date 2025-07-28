"""
build.py (string in → string out)
───────────────────────────────
- run(raw_text: str) → gpt_output(str)
- prompts/fill/*.txt 사용
- 최신 OpenAI API 사용 (클래스 내부에서 직접 GPT 호출)
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import glob
import os
from openai import OpenAI


class BuildStep:
    """
    Step 1: Fill Prompts 실행 모듈
    Input  : 하나의 문자열(raw_text)
    Output : GPT 응답을 합친 하나의 문자열
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.prompt_dir = Path(__file__).resolve().parent.parent / "prompts" / "fill"
        self.client = OpenAI()

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. "
                "export OPENAI_API_KEY='sk-...' 로 설정하세요."
            )

    # ─────────────────────────────
    def load_prompts(self) -> List[Tuple[str, str]]:
        """
        prompts/fill/*.txt → [(prompt_id, 템플릿)] 리스트
        """
        paths = sorted(glob.glob(str(self.prompt_dir / "*_fill_prompt.txt")))
        if not paths:
            raise FileNotFoundError(f"프롬프트 없음: {self.prompt_dir}")
        return [
            (Path(p).stem.replace("_fill_prompt", ""), Path(p).read_text(encoding="utf-8"))
            for p in paths
        ]

    # ─────────────────────────────
    def call_gpt(self, prompt: str) -> str:
        """
        최신 OpenAI API를 사용해 GPT 응답 생성.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            top_p=0.3
        )
        return response.choices[0].message.content.strip()

    # ─────────────────────────────
    def run(self, raw_text: str) -> str:
        """
        string → string
        모든 fill 프롬프트 실행 결과를 합쳐 반환.
        """
        prompts = self.load_prompts()
        outputs = []

        for pid, tmpl in prompts:
            print(f"[BuildStep] ▶ {pid} 실행 중...")
            prompt = tmpl.replace("{INPUT}", raw_text)
            gpt_output = self.call_gpt(prompt)
            outputs.append(f"### {pid}\n{gpt_output}")

        return "\n\n".join(outputs)


# ─────────────────────────────
if __name__ == "__main__":
    infile = "sample/example.txt"
    outfile = "sample/step1_result.txt"

    raw_text = Path(infile).read_text(encoding="utf-8")

    build_step = BuildStep(model="gpt-4o")
    result_text = build_step.run(raw_text)

    # 파일 저장 (검증용)
    Path(outfile).write_text(result_text, encoding="utf-8")
    print(f"[BuildStep] 완료! 결과 저장 → {outfile}")

    # 미리보기
    print("\n=== Preview ===")
    print(result_text[:500], "...")
