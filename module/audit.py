"""
audit.py
───────────────────────────────
USENIX 기준 점검:
- split 결과 (섹션 → 내용)
- tree (구조화 정보)
- prompts/USENIX/*.txt 기반 GPT 호출
"""

from __future__ import annotations
from pathlib import Path
import os
import json
import glob
from typing import Dict
from openai import OpenAI
from split import run as split_run  # 개선된 split.py (dict 반환)


class AuditStep:
    """
    USENIX 검증 모듈
    Input : {섹션명: 내용}, tree dict
    Output: USENIX 평가 보고서(string)
    """

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.prompt_dir = Path(__file__).resolve().parent.parent / "prompts" / "USENIX"
        self.client = OpenAI()

        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY 환경 변수가 필요합니다.")

        #  기준별 섹션 매핑
        self.section_map = {
            "BackgroundClarity": ["Introduction", "Related Work"],
            "Contribution": ["Introduction", "Related Work", "Method"],
            "GapValidation": ["Introduction", "Related Work"],
            "Lesson": ["Discussion", "Conclusion"],
            "Robustness": ["Method"]  # Experiment는 제외 (split에서 삭제됨)
        }

    # ─────────────────────────────
    def load_prompts(self) -> Dict[str, str]:
        paths = sorted(glob.glob(str(self.prompt_dir / "*.txt")))
        if not paths:
            raise FileNotFoundError(f"USENIX 프롬프트 없음: {self.prompt_dir}")
        return {Path(p).stem: Path(p).read_text(encoding="utf-8") for p in paths}

    # ─────────────────────────────
    def call_gpt(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    # ─────────────────────────────
    def run(self, sections: Dict[str, str], tree_dict: Dict[str, dict]) -> str:
        """
        기준별로 관련 섹션 묶어 GPT 호출
        """
        prompts = self.load_prompts()
        outputs = []

        for pname, template in prompts.items():
            target_sections = self.section_map.get(pname, [])

            #  섹션 내용 합치기
            combined_text = ""
            combined_tree = {}
            for sec in target_sections:
                text = sections.get(sec, "")
                if text:
                    combined_text += f"\n\n## {sec}\n{text}"
                    combined_tree[sec] = tree_dict.get(sec.lower(), {})

            if not combined_text.strip():
                continue  # 해당 기준에 들어갈 섹션이 없으면 스킵

            #  프롬프트 생성
            prompt = (
                template.replace("{SECTION_TEXT}", combined_text.strip())
                        .replace("{TREE_INFO}", json.dumps(combined_tree, ensure_ascii=False, indent=2))
                        .replace("{SECTION_NAME}", pname)
            )

            print(f"[AuditStep] ▶ {pname} ({', '.join(target_sections)}) 점검 실행...")
            gpt_output = self.call_gpt(prompt)
            outputs.append(f"# {pname}\n{gpt_output}")

        return "\n\n".join(outputs)


# ─────────────────────────────
if __name__ == "__main__":
    infile_text = "sample/example.txt"         # 원문
    infile_tree = "sample/step2_result.txt"    # 트리(JSON)
    outfile = "sample/step3_result.txt"

    # split 실행 (섹션별 전체 텍스트 딕셔너리)
    raw_text = Path(infile_text).read_text(encoding="utf-8")
    sections = split_run(raw_text, out_file=None)  # {섹션명: 텍스트}

    # 트리 로드
    tree_dict = json.loads(Path(infile_tree).read_text(encoding="utf-8"))

    # USENIX 점검
    step = AuditStep()
    result_text = step.run(sections, tree_dict)

    # 저장
    Path(outfile).write_text(result_text, encoding="utf-8")
    print(f"[AuditStep]  완료! 결과 저장 → {outfile}")

    print("\n=== Preview ===")
    print(result_text[:500], "...")
