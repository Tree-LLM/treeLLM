"""
TreeLLM 로컬 전용 테스트 (API 키 불필요)
========================================
Split과 Fuse 모듈만 테스트하는 경량 버전
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import traceback

sys.path.append(str(Path(__file__).parent.parent))
from config import TreeLLMConfig, load_config
from module.split import run as split_run
from module.fuse import TreeBuilder


class LocalOnlyTester:
    """API 키가 필요없는 모듈만 테스트"""
    
    def __init__(self):
        self.sample_dir = Path("sample")
        self.sample_text = self._load_sample_text()
        self.results = {}
    
    def _load_sample_text(self) -> str:
        """샘플 텍스트 로드"""
        sample_file = self.sample_dir / "example.txt"
        
        if sample_file.exists():
            return sample_file.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"Sample file not found: {sample_file}")
    
    def test_split_module(self, config: TreeLLMConfig = None) -> Dict[str, Any]:
        """Split 모듈 테스트 (API 불필요)"""
        print("\n[1/2] Testing Split Module (No API needed)...")
        start_time = time.time()
        
        try:
            # Split 실행
            sections = split_run(self.sample_text)
            
            # 결과 분석
            num_sections = len([s for s in sections.values() if s])
            section_names = list(sections.keys())
            avg_length = sum(len(s) for s in sections.values() if s) / max(num_sections, 1)
            
            # 품질 평가
            quality_score = self._evaluate_split_quality(sections)
            
            result = {
                "success": True,
                "num_sections": num_sections,
                "sections": section_names,
                "avg_section_length": avg_length,
                "execution_time": time.time() - start_time,
                "quality_score": quality_score,
                "details": {
                    "total_chars": sum(len(s) for s in sections.values()),
                    "longest_section": max(section_names, key=lambda k: len(sections[k])),
                    "shortest_section": min(section_names, key=lambda k: len(sections[k]) if sections[k] else float('inf'))
                }
            }
            
            print(f"✓ Split completed: {num_sections} sections found")
            for i, name in enumerate(section_names[:5]):  # 처음 5개만 표시
                print(f"  - {name}: {len(sections[name])} chars")
            if len(section_names) > 5:
                print(f"  ... and {len(section_names) - 5} more sections")
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"✗ Split failed: {str(e)}")
        
        return result
    
    def test_fuse_module(self, use_sample_build: bool = True) -> Dict[str, Any]:
        """Fuse 모듈 테스트 (API 불필요)"""
        print("\n[2/2] Testing Fuse Module (No API needed)...")
        start_time = time.time()
        
        try:
            # 샘플 Build 출력 사용
            if use_sample_build and (self.sample_dir / "step1_result.txt").exists():
                build_output = (self.sample_dir / "step1_result.txt").read_text(encoding='utf-8')
                print("  Using existing build output from sample/")
            else:
                # 시뮬레이션된 Build 출력
                build_output = self._simulate_build_output()
                print("  Using simulated build output")
            
            # Fuse 실행
            builder = TreeBuilder()
            tree_json = builder.run(build_output)
            tree_dict = json.loads(tree_json)
            
            # 트리 분석
            tree_stats = self._analyze_tree_structure(tree_dict)
            quality_score = self._evaluate_tree_quality(tree_dict)
            
            result = {
                "success": True,
                "tree_depth": tree_stats["depth"],
                "node_count": tree_stats["nodes"],
                "leaf_count": tree_stats["leaves"],
                "execution_time": time.time() - start_time,
                "quality_score": quality_score,
                "tree_preview": self._get_tree_preview(tree_dict)
            }
            
            print(f"✓ Fuse completed: Tree with depth {tree_stats['depth']}, {tree_stats['nodes']} nodes")
            print(f"  Tree structure preview:")
            print(self._visualize_tree(tree_dict, indent=2))
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"✗ Fuse failed: {str(e)}")
        
        return result
    
    def _simulate_build_output(self) -> str:
        """Build 출력 시뮬레이션"""
        sections = split_run(self.sample_text)
        simulated_output = []
        
        for section_name, content in sections.items():
            if content:
                # 각 섹션에 대한 가상의 GPT 응답 생성
                summary = content[:200] + "..." if len(content) > 200 else content
                simulated_output.append(f"### {section_name}\n{summary}\n")
        
        return "\n".join(simulated_output)
    
    def _evaluate_split_quality(self, sections: Dict) -> float:
        """Split 품질 평가"""
        scores = []
        
        # 1. 섹션 수 적절성 (5-10개가 이상적)
        num_sections = len([s for s in sections.values() if s])
        if 5 <= num_sections <= 10:
            scores.append(1.0)
        elif 3 <= num_sections <= 15:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # 2. 섹션 길이 균형
        lengths = [len(s) for s in sections.values() if s]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            std_dev = (sum((l - avg_length) ** 2 for l in lengths) / len(lengths)) ** 0.5
            balance_score = 1.0 / (1.0 + std_dev / avg_length)
            scores.append(balance_score)
        
        # 3. 주요 섹션 포함 여부
        important_sections = ["abstract", "introduction", "method", "result", "conclusion"]
        section_names_lower = [name.lower() for name in sections.keys()]
        found_important = sum(1 for sec in important_sections if any(sec in name for name in section_names_lower))
        scores.append(found_important / len(important_sections))
        
        return sum(scores) / len(scores)
    
    def _analyze_tree_structure(self, tree: Dict) -> Dict[str, int]:
        """트리 구조 분석"""
        stats = {"depth": 0, "nodes": 0, "leaves": 0}
        
        def traverse(node, depth=0):
            stats["nodes"] += 1
            stats["depth"] = max(stats["depth"], depth)
            
            is_leaf = True
            for key, value in node.items():
                if isinstance(value, dict):
                    is_leaf = False
                    traverse(value, depth + 1)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            is_leaf = False
                            traverse(item, depth + 1)
            
            if is_leaf:
                stats["leaves"] += 1
        
        traverse(tree)
        return stats
    
    def _evaluate_tree_quality(self, tree: Dict) -> float:
        """트리 품질 평가"""
        stats = self._analyze_tree_structure(tree)
        scores = []
        
        # 1. 깊이 적절성 (3-6이 이상적)
        if 3 <= stats["depth"] <= 6:
            scores.append(1.0)
        elif 2 <= stats["depth"] <= 8:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # 2. 노드 수 적절성 (10-50이 이상적)
        if 10 <= stats["nodes"] <= 50:
            scores.append(1.0)
        elif 5 <= stats["nodes"] <= 100:
            scores.append(0.7)
        else:
            scores.append(0.4)
        
        # 3. 균형성 (leaves/nodes 비율)
        if stats["nodes"] > 0:
            leaf_ratio = stats["leaves"] / stats["nodes"]
            balance_score = 1.0 - abs(0.5 - leaf_ratio)
            scores.append(balance_score)
        
        return sum(scores) / len(scores)
    
    def _get_tree_preview(self, tree: Dict, max_depth: int = 3) -> str:
        """트리 미리보기"""
        def preview_node(node, depth=0):
            if depth >= max_depth:
                return "..."
            
            items = []
            for key, value in node.items():
                if isinstance(value, dict):
                    items.append(f"{key}: {preview_node(value, depth + 1)}")
                elif isinstance(value, str):
                    preview = value[:50] + "..." if len(value) > 50 else value
                    items.append(f"{key}: {preview}")
                else:
                    items.append(f"{key}: {type(value).__name__}")
            
            return "{" + ", ".join(items[:3]) + ("..." if len(items) > 3 else "") + "}"
        
        return preview_node(tree)
    
    def _visualize_tree(self, tree: Dict, indent: int = 0, max_depth: int = 3) -> str:
        """트리 시각화"""
        lines = []
        
        def traverse(node, prefix="", depth=0):
            if depth >= max_depth:
                lines.append(prefix + "...")
                return
            
            for i, (key, value) in enumerate(node.items()):
                is_last = i == len(node) - 1
                
                if isinstance(value, dict):
                    lines.append(prefix + ("└── " if is_last else "├── ") + str(key))
                    traverse(value, prefix + ("    " if is_last else "│   "), depth + 1)
                else:
                    value_str = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                    lines.append(prefix + ("└── " if is_last else "├── ") + f"{key}: {value_str}")
        
        traverse(tree, "  ")
        return "\n".join(lines)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """모든 로컬 테스트 실행"""
        print("\n" + "="*60)
        print("TreeLLM Local-Only Test (No API Key Required)")
        print("="*60)
        
        all_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "modules": {}
        }
        
        # 1. Split 테스트
        all_results["modules"]["split"] = self.test_split_module()
        
        # 2. Fuse 테스트
        all_results["modules"]["fuse"] = self.test_fuse_module()
        
        # 요약
        success_count = sum(1 for m in all_results["modules"].values() if m.get("success", False))
        total_count = len(all_results["modules"])
        
        print("\n" + "="*60)
        print("Summary:")
        print(f"  Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
        print(f"  Total Time: {sum(m.get('execution_time', 0) for m in all_results['modules'].values()):.2f}s")
        print(f"  Average Quality: {sum(m.get('quality_score', 0) for m in all_results['modules'].values())/total_count:.2f}")
        
        # 결과 저장
        result_dir = Path("test_results")
        result_dir.mkdir(exist_ok=True)
        result_file = result_dir / f"local_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {result_file}")
        
        return all_results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test TreeLLM modules without API key")
    parser.add_argument("--module", choices=["split", "fuse", "all"], default="all",
                       help="Module to test")
    
    args = parser.parse_args()
    
    tester = LocalOnlyTester()
    
    if args.module == "split":
        result = tester.test_split_module()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    elif args.module == "fuse":
        result = tester.test_fuse_module()
        print(f"\nResult: {json.dumps(result, indent=2)}")
    else:
        tester.run_all_tests()
