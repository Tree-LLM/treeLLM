"""
orchestrator.py
───────────────────────────────
전체 파이프라인 실행 + 단계별 파일 저장 + 로그 기록
"""

from pathlib import Path
import json
from datetime import datetime
import os

# 각 단계 모듈 불러오기
from module.build import BuildStep
from module.split import run as split_run
from module.build import BuildStep
from module.fuse import TreeBuilder
from module.audit import AuditStep
from module.edit_pass1 import EditPass1
from module.global_check import GlobalCheck
from module.edit_pass2 import EditPass2


LOG_FILE = Path("sample/orchestrator_log.txt")


class Orchestrator:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model

    def log(self, message: str):
        print(message)
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now()}] {message}\n")

    def run(self, infile_text: str):
        # 로그 초기화
        LOG_FILE.write_text(f"[Orchestrator Started] {datetime.now()}\n\n", encoding="utf-8")

        base_dir = Path("sample")
        base_dir.mkdir(parents=True, exist_ok=True)

        # 단계별 파일 경로
        split_json = base_dir / "step1_result.json"
        split_txt = base_dir / "sample_split.txt"
        build_txt = base_dir / "step1_result.txt"
        tree_json = base_dir / "step2_result.json"
        audit_txt = base_dir / "step3_result.txt"
        edit1_json = base_dir / "step4_result.json"
        global_check_txt = base_dir / "step5_global_check.txt"
        edit2_txt = base_dir / "step6_result.txt"
        final_txt = base_dir / "final_result.txt"

        # ✅ 1. Split
        raw_text = Path(infile_text).read_text(encoding="utf-8")
        sections = split_run(raw_text, out_file=split_txt)
        split_json.write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"[Step 1] Split 완료 → {split_json}, {split_txt}")

        # ✅ 2. Build
        build_step = BuildStep(model=self.model)
        build_result = build_step.run(raw_text)
        build_txt.write_text(build_result, encoding="utf-8")
        self.log(f"[Step 2] Build 완료 → {build_txt}")

        # ✅ 3. Fuse (TreeBuilder)
        builder = TreeBuilder()
        tree_result = builder.run(build_result)
        tree_json.write_text(tree_result, encoding="utf-8")
        self.log(f"[Step 3] TreeBuilder 완료 → {tree_json}")

        # ✅ 4. Audit
        tree_dict = json.loads(tree_result)
        audit_step = AuditStep()
        audit_result = audit_step.run(sections, tree_dict)
        audit_txt.write_text(audit_result, encoding="utf-8")
        self.log(f"[Step 4] Audit 완료 → {audit_txt}")

        # ✅ 5. EditPass1
        edit1_step = EditPass1()
        edit1_result = edit1_step.run(sections, audit_result)
        edit1_json.write_text(json.dumps(edit1_result, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"[Step 5] EditPass1 완료 → {edit1_json}")

        # ✅ 6. GlobalCheck
        global_check = GlobalCheck()
        global_check_result = global_check.run(edit1_result)
        global_check_txt.write_text(global_check_result, encoding="utf-8")
        self.log(f"[Step 6] GlobalCheck 완료 → {global_check_txt}")

        # ✅ 7. EditPass2
        edit2_step = EditPass2()
        edit2_result = edit2_step.run(json.dumps(edit1_result, ensure_ascii=False), global_check_result)
        edit2_txt.write_text(edit2_result, encoding="utf-8")
        self.log(f"[Step 7] EditPass2 완료 → {edit2_txt}")

        # ✅ 8. Final Output (EditPass2 결과 복사)
        final_txt.write_text(edit2_result, encoding="utf-8")
        self.log(f"[Step 8] Finalize 완료 → {final_txt}")

        self.log("[Orchestrator] ✅ 전체 파이프라인 완료!")
        return final_txt.read_text(encoding="utf-8")


if __name__ == "__main__":
    orchestrator = Orchestrator()
    final_text = orchestrator.run("sample/example.txt")

    print("\n=== 최종 논문 미리보기 ===")
    print(final_text[:1000], "...")
