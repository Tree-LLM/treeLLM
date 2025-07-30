"""
edit_pass1.py
───────────────────────────────
1차 수정: USENIX 피드백 기반 개선안 생성
- 입력: split 결과(sample_split.txt), USENIX 피드백(step3_result.txt)
- 출력: 개선안 JSON(step4_result.json)
"""

from __future__ import annotations
from pathlib import Path
import os
import json
from typing import Dict
from openai import OpenAI


class EditPass1:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.client = OpenAI()
        self.prompt_file = Path(__file__).resolve().parent.parent / "prompts" / "1st_modify" / "Modify.txt"

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

    def run(self, sections: Dict[str, str], feedback_text: str) -> Dict[str, str]:
        template = self.load_template()

        # USENIX 피드백을 기준별로 파싱 → 섹션별 맵핑
        feedback_map = self._parse_feedback(feedback_text)

        revised_sections = {}
        for sec, text in sections.items():
            feedback = feedback_map.get(sec, "No major issues found.")
            prompt = (
                template.replace("{SECTION_NAME}", sec)
                        .replace("{SECTION_TEXT}", text)
                        .replace("{FEEDBACK}", feedback)
            )
            print(f"[EditPass1] ▶ {sec} 개선 중...")
            revised_sections[sec] = self.call_gpt(prompt)

        return revised_sections

    def _parse_feedback(self, feedback_text: str) -> Dict[str, str]:
        """
        USENIX 보고서에서 섹션명 기반으로 피드백 추출
        """
        feedback_map = {}
        current = None
        for line in feedback_text.splitlines():
            if line.startswith("#") and not line.strip().startswith("###"):  # 새 기준
                continue
            if line.startswith("##") and "|" in line:
                current = line.split("|")[-1].strip()
                feedback_map[current] = ""
            elif current:
                feedback_map[current] += line + "\n"
        return feedback_map


# ─────────────────────────────
if __name__ == "__main__":
    infile_split_txt = Path("sample/sample_split.txt")  # 현재 split 결과
    infile_feedback = Path("sample/step3_result.txt")   # USENIX 피드백
    outfile_json = Path("sample/step4_result.json")

    # ✅ 1. split 텍스트 → JSON 변환
    sections_dict: Dict[str, str] = {}
    current_sec = None
    for line in infile_split_txt.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):  # 섹션 헤더
            current_sec = line.replace("#", "").strip()
            sections_dict[current_sec] = ""
        elif current_sec and not line.startswith("##"):  # 본문
            sections_dict[current_sec] += line.strip() + " "

    # ✅ 2. USENIX 피드백 로드
    feedback = infile_feedback.read_text(encoding="utf-8")

    # ✅ 3. GPT 호출
    step = EditPass1()
    revised = step.run(sections_dict, feedback)

    # ✅ 4. 결과 저장
    outfile_json.write_text(json.dumps(revised, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[EditPass1] ✅ 완료! 결과 저장 → {outfile_json}")
