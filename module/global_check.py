"""
global_check.py
───────────────────────────────
전역 점검: EditPass1 결과 기반 글로벌 구조 검토
"""

from __future__ import annotations
from pathlib import Path
import os
import json
from openai import OpenAI


class GlobalCheck:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.client = OpenAI()
        self.prompt_file = Path(__file__).resolve().parent.parent / "prompts" / "global_check" / "global_check.txt"

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY 환경 변수가 필요합니다.")

    def load_template(self) -> str:
        return self.prompt_file.read_text(encoding="utf-8")

    def call_gpt(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def run(self, section_data: dict) -> str:
        order = ["Abstract", "Introduction", "Background", "Related Work", "Method", "Discussion", "Conclusion"]

        full_text = ""
        for sec in order:
            if sec in section_data:
                text = section_data[sec]
                if isinstance(text, dict) and "improved" in text:  # EditPass1 형식
                    text = text["improved"]
                full_text += f"\n\n## {sec}\n{text}"

        prompt_template = self.load_template()
        prompt = prompt_template.replace("{FULL_TEXT}", full_text.strip())

        print("[GlobalCheck] ▶ 전역 점검 실행 중...")
        return self.call_gpt(prompt)


if __name__ == "__main__":
    infile = Path("sample/step4_result.json")  # EditPass1 결과
    outfile = Path("sample/step5_global_check.txt")

    if not infile.exists():
        raise FileNotFoundError(f"입력 파일 없음: {infile}")

    section_data = json.loads(infile.read_text(encoding="utf-8"))

    step = GlobalCheck()
    result = step.run(section_data)

    outfile.write_text(result, encoding="utf-8")
    print(f"[GlobalCheck] ✅ 완료! 결과 저장 → {outfile}")

    print("\n=== Preview ===")
    print(result[:500], "...")
