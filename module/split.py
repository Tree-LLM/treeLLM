"""
Step 1 ― 논문을 섹션·문단 단위로 분할하고 번호를 붙입니다.

사용 예시
--------
>>> from pathlib import Path
>>> from treeLLM.module import split
>>> raw = Path("sample/example.txt").read_text(encoding="utf-8")
>>> paragraphs = split.run(raw, out_file="sample/step1_result.txt")
>>> print(paragraphs[0])
Paragraph(section='Introduction', pid='Introduction-1', text='...')

결과 파일(sample/step1_result.txt) 형식
-------------------------------------
## Introduction-1
첫 번째 문단 …

## Introduction-2
두 번째 문단 …

(섹션 이름이 없으면 “Unknown”으로 기록)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Paragraph:
    section: str      # ex) "Introduction"
    pid: str          # ex) "Introduction-3"
    text: str         # paragraph content


# ──────────────────────────────────────────────────────────
_HEADING_PATTERNS = [
    # “1 Introduction”, “2.3.1 Method” 등 숫자 헤더
    re.compile(r"^\s*\d+(?:\.\d+)*\s+(.*\S)\s*$", re.I),
    # “Abstract”, “Related Work”, “Conclusion” 등
    re.compile(
        r"^\s*(Abstract|Introduction|Related Work|Background|Method(?:s)?|"
        r"Experiment(?:s)?|Result(?:s)?|Discussion|Conclusion(?:s)?)\s*$",
        re.I,
    ),
]


def _is_heading(line: str) -> Optional[str]:
    """헤더면 정규화된 섹션명(str)을, 아니면 None을 반환."""
    for pat in _HEADING_PATTERNS:
        m = pat.match(line)
        if m:
            return m.group(1).strip().title()
    return None


def _split_paragraphs(raw: str) -> List[str]:
    """빈 줄 기준으로 문단 목록을 구한다."""
    buff, paras = [], []
    for ln in raw.splitlines():
        if ln.strip():            # non-blank
            buff.append(ln.strip())
        elif buff:                # blank after content → flush
            paras.append(" ".join(buff))
            buff = []
    if buff:
        paras.append(" ".join(buff))
    return paras


def run(raw_text: str, *, out_file: str | Path | None = None) -> List[Paragraph]:
    """
    txt → List[Paragraph]

    Parameters
    ----------
    raw_text : str
        원본 논문 텍스트.
    out_file : str | Path | None
        결과를 저장할 경로. 생략하면 파일을 쓰지 않는다.
    """
    current_section = "Unknown"
    paragraphs: List[Paragraph] = []
    section_idx: dict[str, int] = {}

    for raw_para in _split_paragraphs(raw_text):
        # 헤더 탐지 → 섹션 전환(헤더 자체는 문단 목록에서 제외)
        heading = _is_heading(raw_para)
        if heading:
            current_section = heading
            continue

        # 문단 번호 증가
        section_idx[current_section] = section_idx.get(current_section, 0) + 1
        pid = f"{current_section}-{section_idx[current_section]}"
        paragraphs.append(Paragraph(current_section, pid, raw_para))

    # 필요 시 텍스트 파일 저장
    if out_file:
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fp:
            for p in paragraphs:
                fp.write(f"## {p.pid}\n{p.text}\n\n")

    return paragraphs
