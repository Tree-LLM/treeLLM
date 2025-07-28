from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, Optional

# 허용 섹션 리스트
VALID_SECTIONS = {"Abstract", "Introduction", "Related Work", "Background", "Method", "Discussion", "Conclusion"}

_HEADING_PATTERNS = [
    re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+(.*\S)\s*$", re.I),  # 1. Intro
    re.compile(
        r"^\s*(Abstract|Introduction|Related Work|Background|Method(?:s)?|"
        r"Discussion|Conclusion)\s*$",
        re.I,
    ),
]

def _is_heading(line: str) -> Optional[str]:
    for pat in _HEADING_PATTERNS:
        m = pat.match(line)
        if m:
            name = m.group(1).strip().title()
            return name if name in VALID_SECTIONS else None
    return None


def run(raw_text: str, *, out_file: str | Path | None = None) -> Dict[str, str]:
    """
    txt → {섹션명: 전체 내용(문자열)}
    """
    current_section = None
    sections: Dict[str, str] = {}
    buff = []

    def flush():
        if buff and current_section:
            text = " ".join(buff).strip()
            if text:
                sections[current_section] = sections.get(current_section, "") + " " + text
            buff.clear()

    for line in raw_text.splitlines():
        heading = _is_heading(line.strip())
        if heading:
            flush()
            current_section = heading
            continue
        if line.strip():
            if current_section:  # 허용된 섹션에만 내용 추가
                buff.append(line.strip())
    flush()

    # 결과 저장
    if out_file:
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fp:
            for sec in VALID_SECTIONS:
                if sec in sections:
                    fp.write(f"# {sec}\n{sections[sec].strip()}\n\n")

    return {sec: sections.get(sec, "").strip() for sec in VALID_SECTIONS}


if __name__ == "__main__":
    infile = Path("sample/example.txt")
    outfile = Path("sample/sample_split.txt")

    if not infile.exists():
        raise FileNotFoundError(f"입력 파일 없음: {infile}")

    raw_text = infile.read_text(encoding="utf-8")
    sections = run(raw_text, out_file=outfile)

    print(f"[split] ✅ 처리 완료! 남은 섹션: {[k for k,v in sections.items() if v]}")
    print("\n=== Preview ===")
    for sec, text in sections.items():
        if text:
            print(f"## {sec}\n{text[:150]}...\n")
