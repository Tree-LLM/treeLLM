"""
orchestrator.py
───────────────────────────────
전체 파이프라인 실행 + 단계별 파일 저장 + 결과 JSON 반환
"""

from pathlib import Path
import json
from datetime import datetime
import os

# 각 단계 모듈 불러오기
from module.build import BuildStep
from module.split import run as split_run
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

        # 결과 JSON 누적
        result_data = {"steps": []}

        # ✅ 1. Split
        raw_text = Path(infile_text).read_text(encoding="utf-8")
        sections = split_run(raw_text, out_file=split_txt)
        split_json.write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"[Step 1] Split 완료 → {split_json}, {split_txt}")
        result_data["steps"].append({
            "step": 1,
            "name": "Split",
            "files": {
                "split.json": split_json.read_text(encoding="utf-8"),
                "split.txt": split_txt.read_text(encoding="utf-8")
            }
        })

        # ✅ 2. Build
        build_step = BuildStep(model=self.model)
        build_result = build_step.run(raw_text)
        build_txt.write_text(build_result, encoding="utf-8")
        self.log(f"[Step 2] Build 완료 → {build_txt}")
        result_data["steps"].append({
            "step": 2,
            "name": "Build",
            "files": {"step1_result.txt": build_result}
        })

        # ✅ 3. Fuse (TreeBuilder)
        builder = TreeBuilder()
        tree_result = builder.run(build_result)
        tree_json.write_text(tree_result, encoding="utf-8")
        self.log(f"[Step 3] TreeBuilder 완료 → {tree_json}")
        result_data["steps"].append({
            "step": 3,
            "name": "Fuse (TreeBuilder)",
            "files": {"tree.json": tree_result}
        })

        # ✅ 4. Audit
        tree_dict = json.loads(tree_result)
        audit_step = AuditStep()
        audit_result = audit_step.run(sections, tree_dict)
        audit_txt.write_text(audit_result, encoding="utf-8")
        self.log(f"[Step 4] Audit 완료 → {audit_txt}")
        result_data["steps"].append({
            "step": 4,
            "name": "Audit",
            "files": {"audit.txt": audit_result}
        })

        # ✅ 5. EditPass1
        edit1_step = EditPass1()
        edit1_result = edit1_step.run(sections, audit_result)
        edit1_json.write_text(json.dumps(edit1_result, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log(f"[Step 5] EditPass1 완료 → {edit1_json}")
        result_data["steps"].append({
            "step": 5,
            "name": "EditPass1",
            "files": {"edit1.json": json.dumps(edit1_result, indent=2, ensure_ascii=False)}
        })

        # ✅ 6. GlobalCheck
        global_check = GlobalCheck()
        global_check_result = global_check.run(edit1_result)
        global_check_txt.write_text(global_check_result, encoding="utf-8")
        self.log(f"[Step 6] GlobalCheck 완료 → {global_check_txt}")
        result_data["steps"].append({
            "step": 6,
            "name": "GlobalCheck",
            "files": {"global_check.txt": global_check_result}
        })

        # ✅ 7. EditPass2
        edit2_step = EditPass2()
        edit2_result = edit2_step.run(json.dumps(edit1_result, ensure_ascii=False), global_check_result)
        edit2_txt.write_text(edit2_result, encoding="utf-8")
        self.log(f"[Step 7] EditPass2 완료 → {edit2_txt}")
        result_data["steps"].append({
            "step": 7,
            "name": "EditPass2",
            "files": {"edit2.txt": edit2_result}
        })

        # ✅ 8. Final Output (EditPass2 결과 복사)
        final_txt.write_text(edit2_result, encoding="utf-8")
        self.log(f"[Step 8] Finalize 완료 → {final_txt}")

        result_data["final"] = edit2_result
        self.log("[Orchestrator] ✅ 전체 파이프라인 완료!")

        return result_data
    
        # ✅ 새로운 스트리밍 메서드
    def run_stream(self, infile_text: str):
        LOG_FILE.write_text(f"[Orchestrator Started] {datetime.now()}\n\n", encoding="utf-8")

        base_dir = Path("sample")
        base_dir.mkdir(parents=True, exist_ok=True)

        # 파일 경로
        split_json = base_dir / "step1_result.json"
        split_txt = base_dir / "sample_split.txt"
        build_txt = base_dir / "step1_result.txt"
        tree_json = base_dir / "step2_result.json"
        audit_txt = base_dir / "step3_result.txt"
        edit1_json = base_dir / "step4_result.json"
        global_check_txt = base_dir / "step5_global_check.txt"
        edit2_txt = base_dir / "step6_result.txt"
        final_txt = base_dir / "final_result.txt"

        raw_text = Path(infile_text).read_text(encoding="utf-8")

        # ✅ 1. Split
        sections = split_run(raw_text, out_file=split_txt)
        split_json.write_text(json.dumps(sections, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log("[Step 1] Split 완료")
        yield json.dumps({"step": 1, "name": "Split", "content": split_txt.read_text(encoding="utf-8")})

        # ✅ 2. Build
        build_step = BuildStep(model=self.model)
        build_result = build_step.run(raw_text)
        build_txt.write_text(build_result, encoding="utf-8")
        self.log("[Step 2] Build 완료")
        yield json.dumps({"step": 2, "name": "Build", "content": build_result})

        # ✅ 3. Fuse
        builder = TreeBuilder()
        tree_result = builder.run(build_result)
        tree_json.write_text(tree_result, encoding="utf-8")
        self.log("[Step 3] Fuse 완료")
        yield json.dumps({"step": 3, "name": "Fuse", "content": tree_result})

        # ✅ 4. Audit
        tree_dict = json.loads(tree_result)
        audit_step = AuditStep()
        audit_result = audit_step.run(sections, tree_dict)
        audit_txt.write_text(audit_result, encoding="utf-8")
        self.log("[Step 4] Audit 완료")
        yield json.dumps({"step": 4, "name": "Audit", "content": audit_result})

        # ✅ 5. EditPass1
        edit1_step = EditPass1()
        edit1_result = edit1_step.run(sections, audit_result)
        edit1_json.write_text(json.dumps(edit1_result, indent=2, ensure_ascii=False), encoding="utf-8")
        self.log("[Step 5] EditPass1 완료")
        yield json.dumps({"step": 5, "name": "EditPass1", "content": json.dumps(edit1_result, indent=2, ensure_ascii=False)})

        # ✅ 6. GlobalCheck
        global_check = GlobalCheck()
        global_check_result = global_check.run(edit1_result)
        global_check_txt.write_text(global_check_result, encoding="utf-8")
        self.log("[Step 6] GlobalCheck 완료")
        yield json.dumps({"step": 6, "name": "GlobalCheck", "content": global_check_result})

        # ✅ 7. EditPass2
        edit2_step = EditPass2()
        edit2_result = edit2_step.run(json.dumps(edit1_result, ensure_ascii=False), global_check_result)
        edit2_txt.write_text(edit2_result, encoding="utf-8")
        self.log("[Step 7] EditPass2 완료")
        yield json.dumps({"step": 7, "name": "EditPass2", "content": edit2_result})

        # ✅ 최종 결과
        final_txt.write_text(edit2_result, encoding="utf-8")
        self.log("[Step 8] Finalize 완료")
        yield json.dumps({"step": 8, "name": "Finalize", "content": edit2_result})


if __name__ == "__main__":
    orchestrator = Orchestrator()
    final_data = orchestrator.run("sample/example.txt")

    print("\n=== 최종 논문 미리보기 ===")
    print(final_data["final"][:1000], "...")
