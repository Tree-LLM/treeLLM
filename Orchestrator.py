"""
Orchestrator V2 - 하이퍼파라미터 최적화 버전
─────────────────────────────────────────────
TreeLLM 파이프라인 실행 with 세밀한 파라미터 제어
"""

from pathlib import Path
import json
from datetime import datetime
import os
import time
from typing import Dict, Any, Optional, Generator
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
sys.path.append(str(Path(__file__).parent.parent))

# 설정 및 모듈 임포트
from config import TreeLLMConfig, load_config
from module.build import BuildStep
from module.split import run as split_run
from module.fuse import TreeBuilder
from module.audit import AuditStep
from module.edit_pass1 import EditPass1
from module.global_check import GlobalCheck
from module.edit_pass2 import EditPass2


class OrchestratorV2:
    """하이퍼파라미터 최적화가 적용된 Orchestrator"""
    
    def __init__(self, config: TreeLLMConfig = None, preset: str = "balanced"):
        """
        Args:
            config: TreeLLMConfig 인스턴스
            preset: 사전 정의된 설정 프리셋 ("fast", "balanced", "thorough", "research")
        """
        self.config = config or load_config(preset)
        self.config.validate()
        
        # 로깅 설정
        self._setup_logging()
        
        # 결과 디렉토리 설정
        self.base_dir = Path(self.config.result_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 성능 메트릭 초기화
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "step_durations": {},
            "api_calls": 0,
            "total_tokens": 0
        }
    
    def _setup_logging(self):
        """로깅 설정"""
        log_level = getattr(logging, self.config.log_level)
        logging.basicConfig(
            level=log_level,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_dir / "orchestrator.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """통합 로깅"""
        getattr(self.logger, level.lower())(message)
    
    def _save_intermediate(self, step_name: str, content: Any, file_type: str = "json"):
        """중간 결과 저장"""
        if not self.config.save_intermediate_results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{step_name}_{timestamp}.{file_type}"
        filepath = self.base_dir / filename
        
        if file_type == "json":
            filepath.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            filepath.write_text(str(content), encoding="utf-8")
        
        self.log(f"Saved intermediate result: {filename}", "DEBUG")
    
    def _measure_time(self, func):
        """데코레이터: 단계별 실행 시간 측정"""
        def wrapper(*args, **kwargs):
            step_name = func.__name__.replace("_run_", "")
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            self.metrics["step_durations"][step_name] = duration
            self.log(f"{step_name} completed in {duration:.2f}s")
            return result
        return wrapper
    
    def run(self, infile_text: str) -> Dict[str, Any]:
        """동기 실행 모드"""
        self.metrics["start_time"] = datetime.now()
        self.log(f"Starting TreeLLM pipeline with preset: {self.config}")
        
        # 입력 텍스트 로드
        raw_text = Path(infile_text).read_text(encoding="utf-8")
        
        # 결과 데이터 초기화
        result_data = {
            "config": self.config.__dict__,
            "metrics": self.metrics,
            "steps": []
        }
        
        try:
            # 1. Split
            sections = self._run_split(raw_text)
            result_data["steps"].append({
                "step": 1,
                "name": "Split",
                "sections": list(sections.keys()),
                "content": sections
            })
            
            # 2. Build (병렬 처리 옵션)
            build_result = self._run_build(raw_text)
            result_data["steps"].append({
                "step": 2,
                "name": "Build",
                "content": build_result
            })
            
            # 3. Fuse
            tree_result = self._run_fuse(build_result)
            result_data["steps"].append({
                "step": 3,
                "name": "Fuse",
                "content": json.loads(tree_result)
            })
            
            # 4. Audit
            audit_result = self._run_audit(sections, json.loads(tree_result))
            result_data["steps"].append({
                "step": 4,
                "name": "Audit",
                "content": audit_result
            })
            
            # 5. EditPass1
            edit1_result = self._run_edit1(sections, audit_result)
            result_data["steps"].append({
                "step": 5,
                "name": "EditPass1",
                "content": edit1_result
            })
            
            # 6. GlobalCheck
            global_check_result = self._run_global_check(edit1_result)
            result_data["steps"].append({
                "step": 6,
                "name": "GlobalCheck",
                "content": global_check_result
            })
            
            # 7. EditPass2
            final_result = self._run_edit2(edit1_result, global_check_result)
            result_data["steps"].append({
                "step": 7,
                "name": "EditPass2",
                "content": final_result
            })
            
            # 메트릭 업데이트
            self.metrics["end_time"] = datetime.now()
            self.metrics["total_duration"] = (
                self.metrics["end_time"] - self.metrics["start_time"]
            ).total_seconds()
            
            result_data["final"] = final_result
            result_data["metrics"] = self.metrics
            
            # 최종 결과 저장
            self._save_final_results(result_data)
            
            self.log("Pipeline completed successfully!")
            return result_data
            
        except Exception as e:
            self.log(f"Pipeline failed: {str(e)}", "ERROR")
            raise
    
    @_measure_time
    def _run_split(self, raw_text: str) -> Dict[str, str]:
        """문서 분할 실행"""
        self.log("Running Split step...")
        
        # 설정 적용
        sections = split_run(raw_text)
        
        # 설정에 따른 후처리
        if self.config.split.merge_short_sections:
            sections = self._merge_short_sections(sections)
        
        # 길이 제한 적용
        for key, content in sections.items():
            if len(content) < self.config.split.min_section_length:
                self.log(f"Warning: Section '{key}' is too short ({len(content)} chars)", "WARNING")
            elif len(content) > self.config.split.max_section_length:
                sections[key] = content[:self.config.split.max_section_length]
                self.log(f"Truncated section '{key}' to max length", "WARNING")
        
        self._save_intermediate("split", sections)
        return sections
    
    @_measure_time
    def _run_build(self, raw_text: str) -> str:
        """Build 단계 실행 (병렬 처리 지원)"""
        self.log("Running Build step...")
        
        # BuildStep 초기화 (모델 파라미터 적용)
        build_step = BuildStep(model=self.config.model.model_name)
        
        # 기존 call_gpt 메서드 오버라이드하여 설정 적용
        original_call_gpt = build_step.call_gpt
        
        def enhanced_call_gpt(prompt: str, prompt_type: str = None) -> str:
            params = self.config.get_prompt_params(prompt_type) if prompt_type else self.config.get_model_params()
            
            # API 호출 재시도 로직
            for attempt in range(self.config.build.retry_attempts):
                try:
                    response = build_step.client.chat.completions.create(
                        model=self.config.model.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        **params,
                        timeout=self.config.build.timeout
                    )
                    self.metrics["api_calls"] += 1
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    if attempt < self.config.build.retry_attempts - 1:
                        self.log(f"API call failed, retrying... ({attempt + 1}/{self.config.build.retry_attempts})", "WARNING")
                        time.sleep(self.config.build.retry_delay)
                    else:
                        raise
        
        build_step.call_gpt = enhanced_call_gpt
        
        # 병렬 처리 실행
        if self.config.build.parallel_processing:
            result = self._run_build_parallel(build_step, raw_text)
        else:
            result = build_step.run(raw_text)
        
        self._save_intermediate("build", result, "txt")
        return result
    
    def _run_build_parallel(self, build_step: BuildStep, raw_text: str) -> str:
        """Build 단계 병렬 처리"""
        prompts = build_step.load_prompts()
        outputs = [""] * len(prompts)
        
        with ThreadPoolExecutor(max_workers=self.config.build.max_workers) as executor:
            future_to_index = {}
            
            for i, (pid, tmpl) in enumerate(prompts):
                prompt = tmpl.replace("{INPUT}", raw_text)
                future = executor.submit(
                    build_step.call_gpt, 
                    prompt, 
                    pid.replace("_fill_prompt", "")
                )
                future_to_index[future] = (i, pid)
            
            for future in as_completed(future_to_index):
                index, pid = future_to_index[future]
                try:
                    result = future.result()
                    outputs[index] = f"### {pid}\n{result}"
                    self.log(f"Completed: {pid}")
                except Exception as e:
                    self.log(f"Failed: {pid} - {str(e)}", "ERROR")
                    outputs[index] = f"### {pid}\n[ERROR: {str(e)}]"
        
        return "\n\n".join(outputs)
    
    @_measure_time
    def _run_fuse(self, build_result: str) -> str:
        """Tree 구조 생성"""
        self.log("Running Fuse step...")
        
        builder = TreeBuilder()
        
        # 설정 적용을 위한 후처리 훅
        if hasattr(builder, 'run'):
            original_run = builder.run
            
            def enhanced_run(text: str) -> str:
                result = original_run(text)
                
                # 트리 최적화 적용
                if self.config.fuse.optimization_params["enable_pruning"]:
                    result = self._prune_tree(result)
                if self.config.fuse.optimization_params["enable_rebalancing"]:
                    result = self._rebalance_tree(result)
                
                return result
            
            builder.run = enhanced_run
        
        result = builder.run(build_result)
        self._save_intermediate("tree", json.loads(result))
        return result
    
    @_measure_time
    def _run_audit(self, sections: Dict[str, str], tree_dict: Dict) -> str:
        """감사 단계 실행"""
        self.log("Running Audit step...")
        
        audit_step = AuditStep()
        
        # 엄격도 설정 적용
        if hasattr(audit_step, 'strictness_level'):
            audit_step.strictness_level = self.config.audit.strictness_level
        
        result = audit_step.run(sections, tree_dict)
        
        # 점수 계산 및 검증
        if self.config.audit.detailed_feedback:
            score = self._calculate_audit_score(result)
            if score < self.config.audit.score_threshold:
                self.log(f"Warning: Audit score ({score:.2f}) below threshold ({self.config.audit.score_threshold})", "WARNING")
        
        self._save_intermediate("audit", result, "txt")
        return result
    
    @_measure_time
    def _run_edit1(self, sections: Dict[str, str], audit_result: str) -> Dict:
        """첫 번째 편집 단계"""
        self.log("Running EditPass1...")
        
        edit1_step = EditPass1()
        
        # 편집 파라미터 적용
        if hasattr(edit1_step, 'params'):
            edit1_step.params = self.config.edit.edit1_params
        
        result = edit1_step.run(sections, audit_result)
        self._save_intermediate("edit1", result)
        return result
    
    @_measure_time
    def _run_global_check(self, edit1_result: Dict) -> str:
        """전역 일관성 검사"""
        self.log("Running GlobalCheck...")
        
        global_check = GlobalCheck()
        
        # 검사 항목 설정
        if hasattr(global_check, 'check_items'):
            global_check.check_items = self.config.global_check.check_items
        
        result = global_check.run(edit1_result)
        
        # 일관성 점수 확인
        coherence_score = self._calculate_coherence_score(result)
        if coherence_score < self.config.global_check.coherence_threshold:
            self.log(f"Warning: Coherence score ({coherence_score:.2f}) below threshold", "WARNING")
        
        self._save_intermediate("global_check", result, "txt")
        return result
    
    @_measure_time
    def _run_edit2(self, edit1_result: Dict, global_check_result: str) -> str:
        """최종 편집 단계"""
        self.log("Running EditPass2...")
        
        edit2_step = EditPass2()
        
        # 최종 편집 파라미터 적용
        if hasattr(edit2_step, 'params'):
            edit2_step.params = self.config.edit.edit2_params
        
        result = edit2_step.run(json.dumps(edit1_result, ensure_ascii=False), global_check_result)
        
        # 출력 형식 적용
        if self.config.output.output_format == "latex":
            result = self._convert_to_latex(result)
        elif self.config.output.output_format == "html":
            result = self._convert_to_html(result)
        
        self._save_intermediate("final", result, "txt")
        return result
    
    def run_stream(self, infile_text: str) -> Generator[str, None, None]:
        """스트리밍 실행 모드"""
        self.metrics["start_time"] = datetime.now()
        self.log(f"Starting TreeLLM pipeline (streaming) with preset: {self.config}")
        
        raw_text = Path(infile_text).read_text(encoding="utf-8")
        
        try:
            # 1. Split
            yield json.dumps({"step": 1, "name": "Split", "status": "starting"})
            sections = self._run_split(raw_text)
            yield json.dumps({
                "step": 1, 
                "name": "Split", 
                "status": "completed",
                "preview": {k: v[:200] + "..." for k, v in sections.items() if v}
            })
            
            # 2. Build
            yield json.dumps({"step": 2, "name": "Build", "status": "starting"})
            build_result = self._run_build(raw_text)
            yield json.dumps({
                "step": 2,
                "name": "Build",
                "status": "completed",
                "preview": build_result[:500] + "..."
            })
            
            # 3. Fuse
            yield json.dumps({"step": 3, "name": "Fuse", "status": "starting"})
            tree_result = self._run_fuse(build_result)
            yield json.dumps({
                "step": 3,
                "name": "Fuse",
                "status": "completed",
                "preview": tree_result[:500] + "..."
            })
            
            # 4. Audit
            yield json.dumps({"step": 4, "name": "Audit", "status": "starting"})
            audit_result = self._run_audit(sections, json.loads(tree_result))
            yield json.dumps({
                "step": 4,
                "name": "Audit",
                "status": "completed",
                "preview": audit_result[:500] + "..."
            })
            
            # 5. EditPass1
            yield json.dumps({"step": 5, "name": "EditPass1", "status": "starting"})
            edit1_result = self._run_edit1(sections, audit_result)
            yield json.dumps({
                "step": 5,
                "name": "EditPass1",
                "status": "completed",
                "preview": str(edit1_result)[:500] + "..."
            })
            
            # 6. GlobalCheck
            yield json.dumps({"step": 6, "name": "GlobalCheck", "status": "starting"})
            global_check_result = self._run_global_check(edit1_result)
            yield json.dumps({
                "step": 6,
                "name": "GlobalCheck",
                "status": "completed",
                "preview": global_check_result[:500] + "..."
            })
            
            # 7. EditPass2
            yield json.dumps({"step": 7, "name": "EditPass2", "status": "starting"})
            final_result = self._run_edit2(edit1_result, global_check_result)
            yield json.dumps({
                "step": 7,
                "name": "EditPass2",
                "status": "completed",
                "content": final_result
            })
            
            # 메트릭 업데이트
            self.metrics["end_time"] = datetime.now()
            self.metrics["total_duration"] = (
                self.metrics["end_time"] - self.metrics["start_time"]
            ).total_seconds()
            
            yield json.dumps({
                "step": 8,
                "name": "Complete",
                "metrics": self.metrics
            })
            
        except Exception as e:
            self.log(f"Pipeline failed: {str(e)}", "ERROR")
            yield json.dumps({
                "error": str(e),
                "step": "failed"
            })
    
    # 헬퍼 메서드들
    def _merge_short_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """짧은 섹션 병합"""
        merged = {}
        buffer = ""
        buffer_key = ""
        
        for key, content in sections.items():
            if len(content) < self.config.split.min_section_length:
                if buffer_key:
                    buffer += "\n\n" + content
                else:
                    buffer = content
                    buffer_key = key
            else:
                if buffer:
                    merged[buffer_key] = buffer
                    buffer = ""
                    buffer_key = ""
                merged[key] = content
        
        if buffer:
            merged[buffer_key] = buffer
        
        return merged
    
    def _prune_tree(self, tree_json: str) -> str:
        """트리 가지치기"""
        tree = json.loads(tree_json)
        
        def prune_node(node: Dict) -> Optional[Dict]:
            if "content" in node and len(node.get("content", "")) < self.config.fuse.min_node_content_length:
                return None
            
            if "children" in node:
                node["children"] = [prune_node(child) for child in node["children"]]
                node["children"] = [child for child in node["children"] if child]
            
            return node
        
        pruned = prune_node(tree)
        return json.dumps(pruned, ensure_ascii=False)
    
    def _rebalance_tree(self, tree_json: str) -> str:
        """트리 재균형"""
        tree = json.loads(tree_json)
        
        def get_depth(node: Dict) -> int:
            if "children" not in node or not node["children"]:
                return 1
            return 1 + max(get_depth(child) for child in node["children"])
        
        def rebalance_node(node: Dict, max_depth: int) -> Dict:
            current_depth = get_depth(node)
            
            if current_depth > max_depth:
                # 깊이가 너무 깊으면 일부 노드를 병합
                if "children" in node and len(node["children"]) > 1:
                    mid = len(node["children"]) // 2
                    left_children = node["children"][:mid]
                    right_children = node["children"][mid:]
                    
                    node["children"] = [
                        {"type": "merged", "children": left_children},
                        {"type": "merged", "children": right_children}
                    ]
            
            if "children" in node:
                node["children"] = [rebalance_node(child, max_depth) for child in node["children"]]
            
            return node
        
        rebalanced = rebalance_node(tree, self.config.fuse.max_tree_depth)
        return json.dumps(rebalanced, ensure_ascii=False)
    
    def _calculate_audit_score(self, audit_result: str) -> float:
        """감사 점수 계산"""
        # 간단한 휴리스틱 점수 계산
        positive_keywords = ["good", "strong", "clear", "valid", "sound"]
        negative_keywords = ["weak", "unclear", "missing", "insufficient", "poor"]
        
        text_lower = audit_result.lower()
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.5
        
        return positive_count / (positive_count + negative_count)
    
    def _calculate_coherence_score(self, global_check_result: str) -> float:
        """일관성 점수 계산"""
        # 간단한 휴리스틱 점수 계산
        coherence_indicators = ["consistent", "aligned", "coherent", "unified", "integrated"]
        incoherence_indicators = ["inconsistent", "contradictory", "misaligned", "fragmented"]
        
        text_lower = global_check_result.lower()
        coherent_count = sum(1 for indicator in coherence_indicators if indicator in text_lower)
        incoherent_count = sum(1 for indicator in incoherence_indicators if indicator in text_lower)
        
        if coherent_count + incoherent_count == 0:
            return 0.7
        
        return coherent_count / (coherent_count + incoherent_count)
    
    def _convert_to_latex(self, text: str) -> str:
        """LaTeX 형식으로 변환"""
        latex_header = r"""\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{amsmath}
\usepackage{graphicx}
\begin{document}

"""
        latex_footer = r"""
\end{document}"""
        
        # 간단한 변환 규칙
        text = text.replace("#", "\\section{")
        text = text.replace("\n\n", "}\n\n")
        
        return latex_header + text + latex_footer
    
    def _convert_to_html(self, text: str) -> str:
        """HTML 형식으로 변환"""
        html_header = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
h1, h2, h3 { color: #333; }
</style>
</head>
<body>
"""
        html_footer = """</body>
</html>"""
        
        # 간단한 변환 규칙
        lines = text.split("\n")
        html_lines = []
        
        for line in lines:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                content = line.lstrip("#").strip()
                html_lines.append(f"<h{level}>{content}</h{level}>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")
        
        return html_header + "\n".join(html_lines) + html_footer
    
    def _save_final_results(self, result_data: Dict[str, Any]):
        """최종 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 저장
        json_path = self.base_dir / f"result_{timestamp}.json"
        json_path.write_text(json.dumps(result_data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # 최종 논문 저장
        final_path = self.base_dir / f"final_paper_{timestamp}.{self.config.output.output_format}"
        final_path.write_text(result_data["final"], encoding="utf-8")
        
        # 요약 생성 및 저장
        if self.config.output.generate_summary:
            summary = self._generate_summary(result_data["final"])
            summary_path = self.base_dir / f"summary_{timestamp}.txt"
            summary_path.write_text(summary, encoding="utf-8")
        
        self.log(f"Results saved: {json_path}, {final_path}")
    
    def _generate_summary(self, text: str) -> str:
        """요약 생성"""
        # 간단한 요약 생성 (실제로는 LLM 사용)
        lines = text.split("\n")
        summary_lines = []
        
        for line in lines[:20]:  # 처음 20줄만
            if line.strip() and not line.startswith("#"):
                summary_lines.append(line)
                if len(" ".join(summary_lines).split()) > self.config.output.summary_length:
                    break
        
        return " ".join(summary_lines)


# CLI 인터페이스
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TreeLLM Orchestrator V2")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--preset", choices=["fast", "balanced", "thorough", "research"], 
                       default="balanced", help="Configuration preset")
    parser.add_argument("--model", help="Override model name")
    parser.add_argument("--temperature", type=float, help="Override temperature")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--stream", action="store_true", help="Enable streaming mode")
    
    args = parser.parse_args()
    
    # 설정 로드
    overrides = {}
    if args.model:
        overrides["model"] = {"model_name": args.model}
    if args.temperature:
        overrides["model"] = overrides.get("model", {})
        overrides["model"]["temperature"] = args.temperature
    if args.debug:
        overrides["debug_mode"] = True
        overrides["log_level"] = "DEBUG"
    
    config = load_config(args.preset, **overrides)
    
    # Orchestrator 실행
    orchestrator = OrchestratorV2(config)
    
    if args.stream:
        print("Starting streaming mode...")
        for update in orchestrator.run_stream(args.input):
            print(update)
    else:
        result = orchestrator.run(args.input)
        print(f"\n✅ Pipeline completed in {result['metrics']['total_duration']:.2f}s")
        print(f"📊 API calls: {result['metrics']['api_calls']}")
        print(f"📁 Results saved to: {orchestrator.base_dir}")
