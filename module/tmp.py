"""
tmp.py
───────────────────────────────
split.py 모듈 기능만 테스트하기 위한 스크립트
"""

from pathlib import Path
from split import run as split_run, Paragraph

if __name__ == "__main__":
    # 입력 파일 경로
    infile_text = "sample/example.txt"         # 원문 텍스트
    outfile_split = "sample/tmp_split_result.txt"  # 결과 저장 파일

    # 1. 텍스트 읽기
    raw_text = Path(infile_text).read_text(encoding="utf-8")

    # 2. split 실행
    print("[TMP] ▶ split 실행 중...")
    paragraphs = split_run(raw_text, out_file=outfile_split)

    # 3. 콘솔에 일부 출력
    print(f"[TMP] ✅ 완료! {len(paragraphs)}개 문단 분리")
    print("\n=== Preview (첫 5개 문단) ===")
    for p in paragraphs[:5]:
        print(f"[{p.pid}] ({p.section}) {p.text[:60]}...")
    
    # 4. 결과 파일 저장 안내
    print(f"\n[TMP] 결과 파일 저장 → {outfile_split}")
