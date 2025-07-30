"""
edit_pass2.py
───────────────────────────────
2차 수정: GlobalCheck 피드백 기반 전체 논문 개선
"""

from __future__ import annotations
from pathlib import Path
import os
import json
import re
from openai import OpenAI


class EditPass2:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.client = OpenAI()
        self.prompt_file = Path(__file__).resolve().parent.parent / "prompts" / "2nd_modify" / "2nd_modify.txt"

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY 환경 변수가 필요합니다.")

    def load_template(self) -> str:
        return self.prompt_file.read_text(encoding="utf-8")

    def clean_json(self, raw_text: str) -> str:
        """Remove markdown fences (```json ... ```) and return pure JSON"""
        return re.sub(r"^```json|```$", "", raw_text, flags=re.MULTILINE).strip()

    def call_gpt(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    def run(self, edit_pass1_json: str, global_feedback_text: str) -> str:
        # ✅ Load EditPass1 result
        sections = json.loads(edit_pass1_json)

        # ✅ Clean and parse GlobalCheck JSON
        feedback_clean = self.clean_json(global_feedback_text)
        feedback = json.loads(feedback_clean)

        # ✅ Prepare combined sections
        order = ["Abstract", "Introduction", "Background", "Related Work", "Method", "Discussion", "Conclusion"]
        combined_sections = ""
        for sec in order:
            text = sections.get(sec, "")
            if isinstance(text, dict) and "improved" in text:
                text = text["improved"]
            combined_sections += f"\n# {sec}\n{text.strip()}\n"

        # ✅ Prepare prompt
        template = self.load_template()
        prompt = (
            template.replace("{ALL_SECTIONS}", combined_sections.strip())
                    .replace("{ISSUES}", "\n".join(feedback.get("issues", [])))
                    .replace("{SUGGESTIONS}", "\n".join(feedback.get("suggestions", [])))
        )

        print("[EditPass2] ▶ 글로벌 개선 실행 중...")
        return self.call_gpt(prompt)


if __name__ == "__main__":
    infile_edit1 = Path("sample/step4_result.json")       # EditPass1 결과
    infile_feedback = Path("sample/step5_global_check.txt")  # GlobalCheck 결과
    outfile_final = Path("sample/step6_result.txt")

    # ✅ Load files
    edit1_text = infile_edit1.read_text(encoding="utf-8")
    feedback_text = infile_feedback.read_text(encoding="utf-8")

    # ✅ Execute
    step = EditPass2()
    result_text = step.run(edit1_text, feedback_text)

    outfile_final.write_text(result_text, encoding="utf-8")
    print(f"[EditPass2] ✅ 완료! 결과 저장 → {outfile_final}")
    print("\n=== Preview ===")
    print(result_text[:500], "...")
