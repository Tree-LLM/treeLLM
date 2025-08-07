"""
TreeLLM 모듈별 로컬 테스트 스크립트
====================================
각 모듈의 main 함수를 활용한 테스트
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import traceback

# 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from config import TreeLLMConfig, load_config
from module.split import run as split_run
from module.fuse import TreeBuilder
from module.audit import AuditStep
from module.edit_pass1 import EditPass1
from module.global_check import GlobalCheck
from module.edit_pass2 import EditPass2


class ModuleTester:
    """각 모듈을 개별적으로 테스트"""
    
    def __init__(self, sample_dir: str = "sample"):
        self.sample_dir = Path(sample_dir)
        self.results = {}
        self.sample_text = self._load_sample_text()
    
    def _load_sample_text(self) -> str:
        """샘플 텍스트 로드"""
        # 기존 샘플 파일 사용
        sample_file = self.sample_dir / "example.txt"
        
        if sample_file.exists():
            return sample_file.read_text(encoding='utf-8')
        else:
            raise FileNotFoundError(f"Sample file not found: {sample_file}")
    
    def test_split_module(self, config: TreeLLMConfig) -> Dict[str, Any]:
        """Split 모듈 테스트"""
        print("\n[1/6] Testing Split Module...")
        start_time = time.time()
        
        try:
            # Split 실행
            sections = split_run(self.sample_text)
            
            # 결과 분석
            num_sections = len([s for s in sections.values() if s])
            avg_length = sum(len(s) for s in sections.values() if s) / max(num_sections, 1)
            
            result = {
                "success": True,
                "num_sections": num_sections,
                "sections": list(sections.keys()),
                "avg_section_length": avg_length,
                "execution_time": time.time() - start_time,
                "quality_score": self._evaluate_split_quality(sections, config)
            }
            
            print(f"✓ Split completed: {num_sections} sections found")
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"✗ Split failed: {str(e)}")
        
        return result
    
    def test_fuse_module(self, build_output: str = None) -> Dict[str, Any]:
        """Fuse 모듈 테스트"""
        print("\n[2/6] Testing Fuse Module...")
        start_time = time.time()
        
        try:
            # 테스트용 Build 출력 시뮬레이션
            if not build_output:
                build_output = """
### abstract
The paper introduces TreeLLM for document analysis.

### introduction  
TreeLLM processes documents hierarchically for better understanding.

### method
Seven-stage processing pipeline with optimized hyperparameters.
                """
            
            # Fuse 실행
            builder = TreeBuilder()
            tree_json = builder.run(build_output)
            tree_dict = json.loads(tree_json)
            
            result = {
                "success": True,
                "tree_depth": self._calculate_tree_depth(tree_dict),
                "node_count": self._count_nodes(tree_dict),
                "execution_time": time.time() - start_time,
                "quality_score": self._evaluate_tree_quality(tree_dict)
            }
            
            print(f"✓ Fuse completed: Tree with depth {result['tree_depth']}")
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"✗ Fuse failed: {str(e)}")
        
        return result
    
    def test_audit_module(self, sections: Dict = None, tree: Dict = None) -> Dict[str, Any]:
        """Audit 모듈 테스트"""
        print("\n[3/6] Testing Audit Module...")
        start_time = time.time()
        
        try:
            # 테스트용 데이터
            if not sections:
                sections = split_run(self.sample_text)
            if not tree:
                tree = {"root": {"content": "Test tree"}}
            
            # Audit 실행
            audit = AuditStep()
            audit_result = audit.run(sections, tree)
            
            result = {
                "success": True,
                "audit_length": len(audit_result),
                "issues_found": audit_result.count("issue") + audit_result.count("problem"),
                "suggestions": audit_result.count("suggest") + audit_result.count("recommend"),
                "execution_time": time.time() - start_time,
                "quality_score": self._evaluate_audit_quality(audit_result)
            }
            
            print(f"✓ Audit completed: {result['issues_found']} issues, {result['suggestions']} suggestions")
            
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"✗ Audit failed: {str(e)}")
        
        return result
    
    def test_edit_modules(self) -> Dict[str, Any]:
        """Edit 모듈들 테스트"""
        print("\n[4-6] Testing Edit Modules...")
        results = {}
        
        # 테스트 데이터 준비
        sections = split_run(self.sample_text)
        audit_result = "Test audit: Some issues found in methodology section."
        
        # EditPass1 테스트
        try:
            start_time = time.time()
            edit1 = EditPass1()
            edit1_result = edit1.run(sections, audit_result)
            
            results["edit_pass1"] = {
                "success": True,
                "sections_edited": len(edit1_result),
                "execution_time": time.time() - start_time
            }
            print("✓ EditPass1 completed")
            
        except Exception as e:
            results["edit_pass1"] = {"success": False, "error": str(e)}
            print(f"✗ EditPass1 failed: {str(e)}")
        
        # GlobalCheck 테스트
        try:
            start_time = time.time()
            global_check = GlobalCheck()
            gc_result = global_check.run(edit1_result if 'edit1_result' in locals() else {})
            
            results["global_check"] = {
                "success": True,
                "check_length": len(gc_result),
                "execution_time": time.time() - start_time
            }
            print("✓ GlobalCheck completed")
            
        except Exception as e:
            results["global_check"] = {"success": False, "error": str(e)}
            print(f"✗ GlobalCheck failed: {str(e)}")
        
        # EditPass2 테스트
        try:
            start_time = time.time()
            edit2 = EditPass2()
            edit2_result = edit2.run(
                json.dumps(edit1_result if 'edit1_result' in locals() else {}),
                gc_result if 'gc_result' in locals() else ""
            )
            
            results["edit_pass2"] = {
                "success": True,
                "final_length": len(edit2_result),
                "execution_time": time.time() - start_time
            }
            print("✓ EditPass2 completed")
            
        except Exception as e:
            results["edit_pass2"] = {"success": False, "error": str(e)}
            print(f"✗ EditPass2 failed: {str(e)}")
        
        return results
    
    def _evaluate_split_quality(self, sections: Dict, config: TreeLLMConfig) -> float:
        """Split 품질 평가"""
        score = 0.0
        
        # 섹션 수 평가
        num_sections = len([s for s in sections.values() if s])
        if 5 <= num_sections <= 8:
            score += 0.3
        elif 3 <= num_sections <= 10:
            score += 0.2
        
        # 섹션 길이 평가
        lengths = [len(s) for s in sections.values() if s]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            if config.split.min_section_length <= avg_length <= config.split.max_section_length:
                score += 0.4
            
            # 길이 균형 평가
            if max(lengths) / min(lengths) < 10:
                score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_tree_depth(self, tree: Dict) -> int:
        """트리 깊이 계산"""
        def get_depth(node):
            if not isinstance(node, dict) or 'children' not in node:
                return 1
            return 1 + max([get_depth(child) for child in node['children']], default=0)
        
        return get_depth(tree)
    
    def _count_nodes(self, tree: Dict) -> int:
        """노드 수 계산"""
        def count(node):
            if not isinstance(node, dict):
                return 0
            count_sum = 1
            if 'children' in node:
                for child in node['children']:
                    count_sum += count(child)
            return count_sum
        
        return count(tree)
    
    def _evaluate_tree_quality(self, tree: Dict) -> float:
        """트리 품질 평가"""
        depth = self._calculate_tree_depth(tree)
        nodes = self._count_nodes(tree)
        
        # 적절한 깊이 (3-6)
        depth_score = 1.0 if 3 <= depth <= 6 else 0.5
        
        # 적절한 노드 수 (10-50)
        node_score = 1.0 if 10 <= nodes <= 50 else 0.5
        
        return (depth_score + node_score) / 2
    
    def _evaluate_audit_quality(self, audit_result: str) -> float:
        """Audit 품질 평가"""
        # 적절한 길이
        length_score = 1.0 if 500 <= len(audit_result) <= 3000 else 0.5
        
        # 구체적인 피드백 포함
        feedback_score = min(
            (audit_result.count("issue") + audit_result.count("suggest")) / 5,
            1.0
        )
        
        return (length_score + feedback_score) / 2
    
    def run_all_tests(self, config: TreeLLMConfig = None) -> Dict[str, Any]:
        """모든 모듈 테스트 실행"""
        if not config:
            config = load_config("balanced")
        
        print(f"\nTesting TreeLLM Modules with config: {config.model.model_name}")
        print("=" * 60)
        
        # 각 모듈 테스트
        all_results = {
            "config": {
                "model": config.model.model_name,
                "temperature": config.model.temperature,
                "max_tokens": config.model.max_tokens
            },
            "modules": {}
        }
        
        # 1. Split 테스트
        all_results["modules"]["split"] = self.test_split_module(config)
        
        # 2. Fuse 테스트 (Build는 API 필요하므로 스킵)
        all_results["modules"]["fuse"] = self.test_fuse_module()
        
        # 3. Audit 테스트
        all_results["modules"]["audit"] = self.test_audit_module()
        
        # 4-6. Edit 모듈들 테스트
        edit_results = self.test_edit_modules()
        all_results["modules"].update(edit_results)
        
        # 전체 점수 계산
        success_count = sum(
            1 for module in all_results["modules"].values() 
            if module.get("success", False)
        )
        total_count = len(all_results["modules"])
        
        all_results["summary"] = {
            "success_rate": success_count / total_count,
            "total_execution_time": sum(
                module.get("execution_time", 0) 
                for module in all_results["modules"].values()
            ),
            "average_quality_score": sum(
                module.get("quality_score", 0) 
                for module in all_results["modules"].values()
            ) / total_count
        }
        
        # 결과 저장
        self._save_test_results(all_results)
        
        return all_results
    
    def _save_test_results(self, results: Dict[str, Any]):
        """테스트 결과 저장"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        result_dir = Path("test_results")
        result_dir.mkdir(exist_ok=True)
        
        # JSON 저장
        result_file = result_dir / f"module_test_{timestamp}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 읽기 쉬운 보고서
        report_file = result_dir / f"module_test_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("TreeLLM Module Test Report\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Configuration:\n")
            f.write(f"  Model: {results['config']['model']}\n")
            f.write(f"  Temperature: {results['config']['temperature']}\n")
            f.write(f"  Max Tokens: {results['config']['max_tokens']}\n\n")
            
            f.write("Module Test Results:\n")
            f.write("-" * 40 + "\n")
            
            for module_name, module_result in results['modules'].items():
                status = "✓ PASS" if module_result.get('success', False) else "✗ FAIL"
                f.write(f"\n{module_name.upper()}: {status}\n")
                
                if module_result.get('success', False):
                    f.write(f"  Execution Time: {module_result.get('execution_time', 0):.2f}s\n")
                    if 'quality_score' in module_result:
                        f.write(f"  Quality Score: {module_result['quality_score']:.2f}\n")
                else:
                    f.write(f"  Error: {module_result.get('error', 'Unknown error')}\n")
            
            f.write(f"\nSummary:\n")
            f.write(f"  Success Rate: {results['summary']['success_rate']:.1%}\n")
            f.write(f"  Total Time: {results['summary']['total_execution_time']:.2f}s\n")
            f.write(f"  Avg Quality: {results['summary']['average_quality_score']:.2f}\n")
        
        print(f"\n✅ Test results saved to: {result_file}")
        print(f"📄 Report saved to: {report_file}")


def test_different_configs():
    """다양한 설정으로 테스트"""
    tester = ModuleTester()
    
    configs_to_test = [
        ("fast", load_config("fast")),
        ("balanced", load_config("balanced")),
        ("thorough", load_config("thorough")),
        ("custom_low_temp", load_config("balanced", model={"temperature": 0.1})),
        ("custom_high_tokens", load_config("balanced", model={"max_tokens": 8192})),
    ]
    
    all_results = {}
    
    for config_name, config in configs_to_test:
        print(f"\n\n{'='*60}")
        print(f"Testing configuration: {config_name}")
        print(f"{'='*60}")
        
        results = tester.run_all_tests(config)
        all_results[config_name] = results
        
        time.sleep(1)  # 테스트 간 짧은 대기
    
    # 비교 보고서 생성
    comparison_file = Path("test_results") / f"comparison_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write("Configuration Comparison Report\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"{'Config':<15} {'Success':<10} {'Time(s)':<10} {'Quality':<10}\n")
        f.write("-" * 45 + "\n")
        
        for config_name, results in all_results.items():
            summary = results['summary']
            f.write(f"{config_name:<15} "
                   f"{summary['success_rate']:.1%}    "
                   f"{summary['total_execution_time']:<10.2f} "
                   f"{summary['average_quality_score']:<10.2f}\n")
    
    print(f"\n📊 Comparison report saved to: {comparison_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test TreeLLM modules locally")
    parser.add_argument("--config", default="balanced", 
                       choices=["fast", "balanced", "thorough", "research"],
                       help="Configuration preset to test")
    parser.add_argument("--compare", action="store_true",
                       help="Compare different configurations")
    parser.add_argument("--module", help="Test specific module only")
    
    args = parser.parse_args()
    
    if args.compare:
        test_different_configs()
    else:
        tester = ModuleTester()
        config = load_config(args.config)
        
        if args.module:
            # 특정 모듈만 테스트
            if args.module == "split":
                result = tester.test_split_module(config)
            elif args.module == "fuse":
                result = tester.test_fuse_module()
            elif args.module == "audit":
                result = tester.test_audit_module()
            else:
                print(f"Unknown module: {args.module}")
                sys.exit(1)
            
            print(f"\nResult: {json.dumps(result, indent=2)}")
        else:
            # 전체 테스트
            results = tester.run_all_tests(config)
            print(f"\n\nFinal Summary:")
            print(f"Success Rate: {results['summary']['success_rate']:.1%}")
            print(f"Total Time: {results['summary']['total_execution_time']:.2f}s")
            print(f"Average Quality: {results['summary']['average_quality_score']:.2f}")
