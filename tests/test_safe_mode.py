"""
TreeLLM 안전한 테스트 모드 (API 호출 제한)
=========================================
API 키는 있지만 비용을 최소화하면서 테스트
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch

sys.path.append(str(Path(__file__).parent.parent))
from config import TreeLLMConfig, load_config
from module.split import run as split_run
from module.fuse import TreeBuilder
from module.audit import AuditStep
from module.edit_pass1 import EditPass1
from module.global_check import GlobalCheck
from module.edit_pass2 import EditPass2


class SafeTester:
    """API 호출을 제한하거나 모의하는 안전한 테스터"""
    
    def __init__(self, mode: str = "mock"):
        """
        mode: 
        - "mock": API 호출을 완전히 모의 (비용 없음)
        - "cache": 첫 호출만 실제, 이후 캐시 사용
        - "dry_run": API 호출 직전에 중단
        - "minimal": 최소한의 토큰만 사용 (아주 짧은 텍스트)
        """
        self.mode = mode
        self.sample_dir = Path("sample")
        self.cache_dir = Path("test_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.api_call_count = 0
        self.estimated_cost = 0.0
        
        # 기존 샘플 데이터 로드
        self.sample_data = self._load_existing_samples()
    
    def _load_existing_samples(self) -> Dict[str, str]:
        """기존 샘플 결과물 로드"""
        data = {}
        
        # 각 단계별 기존 결과물 로드
        if (self.sample_dir / "step1_result.txt").exists():
            data["build"] = (self.sample_dir / "step1_result.txt").read_text(encoding='utf-8')
        
        if (self.sample_dir / "step3_result.txt").exists():
            data["audit"] = (self.sample_dir / "step3_result.txt").read_text(encoding='utf-8')
        
        if (self.sample_dir / "step4_result.json").exists():
            with open(self.sample_dir / "step4_result.json", 'r', encoding='utf-8') as f:
                data["edit1"] = json.load(f)
        
        if (self.sample_dir / "step5_global_check.txt").exists():
            data["global_check"] = (self.sample_dir / "step5_global_check.txt").read_text(encoding='utf-8')
        
        if (self.sample_dir / "step6_result.txt").exists():
            data["edit2"] = (self.sample_dir / "step6_result.txt").read_text(encoding='utf-8')
        
        return data
    
    def _mock_gpt_response(self, prompt: str, module: str) -> str:
        """GPT 응답 모의"""
        # 기존 샘플 데이터가 있으면 사용
        if module in self.sample_data:
            print(f"  📦 Using cached sample for {module}")
            return self.sample_data[module]
        
        # 없으면 간단한 모의 응답 생성
        responses = {
            "build": f"### Mock Analysis\nThis is a mock response for testing.\nPrompt length: {len(prompt)} chars",
            "audit": "Mock Audit Result:\n- Structure: Good\n- Content: Adequate\n- Suggestions: None",
            "edit": "Mock edited content based on the input.",
            "global_check": "Mock Global Check:\n- Consistency: High\n- Completeness: Good",
        }
        
        return responses.get(module, f"Mock response for {module}")
    
    def _estimate_api_cost(self, prompt: str, response: str, model: str = "gpt-4o") -> float:
        """API 비용 추정"""
        # 토큰 수 추정 (대략적)
        input_tokens = len(prompt) / 4
        output_tokens = len(response) / 4
        
        # 모델별 가격 (2024년 기준 추정치)
        if model == "gpt-4o":
            input_cost = input_tokens * 0.03 / 1000
            output_cost = output_tokens * 0.06 / 1000
        elif model == "gpt-3.5-turbo":
            input_cost = input_tokens * 0.001 / 1000
            output_cost = output_tokens * 0.002 / 1000
        else:
            input_cost = input_tokens * 0.01 / 1000
            output_cost = output_tokens * 0.03 / 1000
        
        return input_cost + output_cost
    
    def test_build_safe(self, text: str, config: TreeLLMConfig) -> Dict[str, Any]:
        """Build 모듈 안전 테스트"""
        print("\n🛡️ Testing Build Module (Safe Mode)...")
        
        if self.mode == "mock":
            # 완전 모의
            print("  🎭 Using mock API responses")
            from module.build import BuildStep
            build_step = BuildStep(model=config.model.model_name)
            
            # API 호출을 가로채기
            with patch.object(build_step, 'call_gpt') as mock_call:
                mock_call.return_value = self._mock_gpt_response(text, "build")
                result = mock_call.return_value
                estimated_cost = 0.0
                
        elif self.mode == "dry_run":
            # API 호출 직전 중단
            print("  🏃 Dry run - stopping before API call")
            result = "[DRY RUN] API call would happen here"
            estimated_cost = self._estimate_api_cost(text, "typical response", config.model.model_name)
            print(f"  💰 Estimated cost: ${estimated_cost:.4f}")
            
        elif self.mode == "minimal":
            # 최소 텍스트로만 실제 호출
            print("  🔬 Using minimal text for real API call")
            mini_text = text[:500]  # 500자만 사용
            
            from module.build import BuildStep
            build_step = BuildStep(model=config.model.model_name)
            
            # 프롬프트 수를 1개로 제한
            print("  ⚠️  Real API call with minimal data - cost will incur!")
            response = input("  Continue? (y/N): ")
            
            if response.lower() == 'y':
                # 실제 호출 (최소한만)
                result = build_step.call_gpt(f"Summarize briefly: {mini_text}")
                estimated_cost = self._estimate_api_cost(mini_text, result, config.model.model_name)
                self.api_call_count += 1
                self.estimated_cost += estimated_cost
            else:
                print("  ❌ Cancelled by user")
                return {"success": False, "cancelled": True}
        
        elif self.mode == "cache":
            # 캐시 확인
            cache_file = self.cache_dir / "build_cache.json"
            
            if cache_file.exists():
                print("  📂 Using cached response")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    result = cache_data["response"]
                    estimated_cost = 0.0
            else:
                print("  ⚠️  No cache found. Use 'minimal' mode for first run.")
                return {"success": False, "error": "No cache available"}
        
        return {
            "success": True,
            "result": result,
            "estimated_cost": estimated_cost,
            "api_calls": self.api_call_count,
            "mode": self.mode
        }
    
    def test_all_modules_safe(self, config: TreeLLMConfig = None) -> Dict[str, Any]:
        """모든 모듈 안전 테스트"""
        if not config:
            config = load_config("balanced")
        
        print(f"\n{'='*60}")
        print(f"TreeLLM Safe Test Mode: {self.mode.upper()}")
        print(f"Model: {config.model.model_name}")
        print(f"{'='*60}")
        
        results = {}
        
        # 1. Split (API 불필요)
        print("\n[1/6] Split Module (No API needed)")
        sample_text = (self.sample_dir / "example.txt").read_text(encoding='utf-8')
        sections = split_run(sample_text)
        results["split"] = {
            "success": True,
            "sections": len(sections),
            "cost": 0.0
        }
        print(f"✓ Split: {len(sections)} sections")
        
        # 2. Build (API 필요 - 안전 모드)
        print("\n[2/6] Build Module")
        build_result = self.test_build_safe(sample_text, config)
        results["build"] = build_result
        
        # 3. Fuse (API 불필요)
        print("\n[3/6] Fuse Module (No API needed)")
        if build_result["success"]:
            builder = TreeBuilder()
            tree_json = builder.run(build_result["result"])
            results["fuse"] = {
                "success": True,
                "cost": 0.0
            }
            print("✓ Fuse: Tree structure created")
        
        # 4-6. 나머지 모듈들은 모의만
        for i, module in enumerate(["audit", "edit1", "global_check", "edit2"], 4):
            print(f"\n[{i}/6] {module.title()} Module")
            if self.mode == "mock":
                results[module] = {
                    "success": True,
                    "result": f"Mock {module} result",
                    "cost": 0.0
                }
                print(f"✓ {module}: Mocked")
            else:
                results[module] = {
                    "success": False,
                    "skipped": True,
                    "reason": f"Skipped in {self.mode} mode to save costs"
                }
                print(f"⏭️  {module}: Skipped to save costs")
        
        # 요약
        print(f"\n{'='*60}")
        print("Test Summary:")
        print(f"  Mode: {self.mode}")
        print(f"  Total API calls: {self.api_call_count}")
        print(f"  Total estimated cost: ${self.estimated_cost:.4f}")
        print(f"  Modules tested: {sum(1 for r in results.values() if r.get('success', False))}/{len(results)}")
        
        return results
    
    def run_cost_analysis(self, config: TreeLLMConfig = None) -> Dict[str, float]:
        """전체 파이프라인 비용 분석 (실제 호출 없이)"""
        if not config:
            config = load_config("balanced")
        
        print("\n💰 Cost Analysis for Full Pipeline")
        print("="*50)
        
        # 샘플 텍스트 기준
        sample_text = (self.sample_dir / "example.txt").read_text(encoding='utf-8')
        text_length = len(sample_text)
        
        # 각 단계별 예상 비용
        costs = {}
        
        # Build: 7개 프롬프트
        build_prompts = 7
        avg_prompt_length = text_length + 500  # 텍스트 + 프롬프트 템플릿
        avg_response_length = config.model.max_tokens
        
        build_cost = build_prompts * self._estimate_api_cost(
            "x" * avg_prompt_length,
            "x" * avg_response_length,
            config.model.model_name
        )
        costs["build"] = build_cost
        
        # Audit
        audit_prompt_length = text_length + 2000  # 섹션들 + 트리
        costs["audit"] = self._estimate_api_cost(
            "x" * audit_prompt_length,
            "x" * 2000,
            config.model.model_name
        )
        
        # Edit Pass 1
        costs["edit1"] = len(sections) * self._estimate_api_cost(
            "x" * 1000,
            "x" * 1000,
            config.model.model_name
        ) if 'sections' in locals() else build_cost * 0.5
        
        # Global Check
        costs["global_check"] = self._estimate_api_cost(
            "x" * text_length,
            "x" * 1500,
            config.model.model_name
        )
        
        # Edit Pass 2
        costs["edit2"] = self._estimate_api_cost(
            "x" * text_length,
            "x" * text_length,
            config.model.model_name
        )
        
        total_cost = sum(costs.values())
        
        # 결과 출력
        print(f"\nModel: {config.model.model_name}")
        print(f"Max Tokens: {config.model.max_tokens}")
        print(f"Text Length: {text_length:,} characters")
        print(f"\nEstimated Costs by Module:")
        print("-" * 40)
        
        for module, cost in costs.items():
            print(f"{module:<15}: ${cost:>8.4f}")
        
        print("-" * 40)
        print(f"{'TOTAL':<15}: ${total_cost:>8.4f}")
        
        # 프리셋별 비교
        print(f"\n\nCost Comparison by Preset:")
        print("-" * 50)
        print(f"{'Preset':<12} {'Model':<15} {'Cost':<10}")
        print("-" * 50)
        
        for preset in ["fast", "balanced", "thorough", "research"]:
            preset_config = load_config(preset)
            preset_build_cost = build_prompts * self._estimate_api_cost(
                "x" * avg_prompt_length,
                "x" * preset_config.model.max_tokens,
                preset_config.model.model_name
            )
            preset_total = preset_build_cost * 2.5  # 대략적인 전체 비용
            
            print(f"{preset:<12} {preset_config.model.model_name:<15} ${preset_total:<10.4f}")
        
        return costs


def create_test_cache():
    """테스트용 캐시 생성 (기존 샘플 데이터 활용)"""
    cache_dir = Path("test_cache")
    cache_dir.mkdir(exist_ok=True)
    
    sample_dir = Path("sample")
    
    # Build 캐시
    if (sample_dir / "step1_result.txt").exists():
        build_cache = {
            "prompt_hash": "sample",
            "response": (sample_dir / "step1_result.txt").read_text(encoding='utf-8'),
            "timestamp": time.time()
        }
        
        with open(cache_dir / "build_cache.json", 'w', encoding='utf-8') as f:
            json.dump(build_cache, f, ensure_ascii=False)
        
        print("✓ Created build cache from existing samples")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe testing without API costs")
    parser.add_argument("--mode", choices=["mock", "cache", "dry_run", "minimal"], 
                       default="mock", help="Testing mode")
    parser.add_argument("--analyze-cost", action="store_true", 
                       help="Show cost analysis only")
    parser.add_argument("--create-cache", action="store_true",
                       help="Create test cache from samples")
    parser.add_argument("--config", default="balanced",
                       choices=["fast", "balanced", "thorough", "research"])
    
    args = parser.parse_args()
    
    if args.create_cache:
        create_test_cache()
    elif args.analyze_cost:
        tester = SafeTester()
        config = load_config(args.config)
        tester.run_cost_analysis(config)
    else:
        tester = SafeTester(mode=args.mode)
        config = load_config(args.config)
        results = tester.test_all_modules_safe(config)
        
        # 결과 저장
        result_file = Path("test_results") / f"safe_test_{args.mode}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        result_file.parent.mkdir(exist_ok=True)
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved to: {result_file}")
