import json
import re
from pathlib import Path
from typing import Dict


class TreeBuilder:
    """
    GPT 없이, 섹션별 JSON 블록을 정리된 트리(dict)로 병합
    Input  : string
    Output : JSON string
    """

    def __init__(self):
        self.pattern = re.compile(r"^###\s+([a-zA-Z_]+)\s*$", re.MULTILINE)

    def clean_json_block(self, text: str) -> str:
        """
        ```json ... ``` 블록 제거
        """
        return re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

    def run(self, raw_text: str) -> str:
        matches = list(self.pattern.finditer(raw_text))
        tree: Dict[str, dict] = {}

        for i, match in enumerate(matches):
            section_name = match.group(1).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
            block = raw_text[start:end].strip()
            cleaned = self.clean_json_block(block)

            try:
                parsed = json.loads(cleaned)
                # 키를 소문자로 정규화
                tree[section_name.lower()] = parsed
            except json.JSONDecodeError:
                print(f"[TreeBuilder] JSON 파싱 실패: {section_name}")
                continue

        return json.dumps(tree, indent=2, ensure_ascii=False)


# 테스트 실행
if __name__ == "__main__":
    infile = "sample/step1_result.txt"
    outfile = "sample/step2_result.txt"

    raw_text = Path(infile).read_text(encoding="utf-8")
    builder = TreeBuilder()
    result_text = builder.run(raw_text)

    Path(outfile).write_text(result_text, encoding="utf-8")
    print(f"[TreeBuilder] ✅ 병합 완료 → {outfile}")

    print("\n=== Preview ===")
    print(result_text[:500], "...")
