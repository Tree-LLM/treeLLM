"""
TreeLLM 기존 샘플 데이터를 활용한 하이퍼파라미터 테스트
========================================================
API 호출 없이 기존 중간 결과물을 활용하여 테스트
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

from config import TreeLLMConfig, load_config, PRESETS


class EfficientTester:
    """기존 샘플 데이터를 활용한 효율적인 테스터"""
    
    def __init__(self):
        self.sample_dir = Path("sample")
        self.init_sample_dir = Path("init_sample")
        
        # 기존 데이터 로드
        self.sample_data = self._load_existing_data()
        
    def _load_existing_data(self) -> Dict[str, any]:
        """기존 샘플 데이터 로드"""
        data = {}
        
        # 원본 텍스트
        if (self.sample_dir / "example.txt").exists():
            data["original_text"] = (self.sample_dir / "example.txt").read_text(encoding='utf-8')
        
        # Split 결과
        if (self.sample_dir / "step1_result.json").exists():
            with open(self.sample_dir / "step1_result.json", 'r', encoding='utf-8') as f:
                data["split_result"] = json.load(f)
        
        # Build 결과
        if (self.sample_dir / "step1_result.txt").exists():
            data["build_result"] = (self.sample_dir / "step1_result.txt").read_text(encoding='utf-8')
        
        # Tree 결과
        if (self.sample_dir / "step2_result.json").exists():
            with open(self.sample_dir / "step2_result.json", 'r', encoding='utf-8') as f:
                data["tree_result"] = json.load(f)
        
        # Audit 결과
        if (self.sample_dir / "step3_result.txt").exists():
            data["audit_result"] = (self.sample_dir / "step3_result.txt").read_text(encoding='utf-8')
        
        # Edit1 결과
        if (self.sample_dir / "step4_result.json").exists():
            with open(self.sample_dir / "step4_result.json", 'r', encoding='utf-8') as f:
                data["edit1_result"] = json.load(f)
        
        # Global Check 결과
        if (self.sample_dir / "step5_global_check.txt").exists():
            data["global_check_result"] = (self.sample_dir / "step5_global_check.txt").read_text(encoding='utf-8')
        
        # Final 결과
        if (self.sample_dir / "step6_result.txt").exists():
            data["final_result"] = (self.sample_dir / "step6_result.txt").read_text(encoding='utf-8')
        
        return data
    
    def analyze_with_config(self, config: TreeLLMConfig) -> Dict[str, float]:
        """특정 설정으로 샘플 데이터 분석"""
        scores = {}
        
        # 1. Split 품질 분석
        if "split_result" in self.sample_data:
            scores["split_quality"] = self._analyze_split_quality(
                self.sample_data["split_result"], 
                config
            )
        
        # 2. Build 출력 분석 (토큰 사용량 추정)
        if "build_result" in self.sample_data:
            scores["token_efficiency"] = self._estimate_token_usage(
                self.sample_data["build_result"],
                config
            )
        
        # 3. Tree 구조 분석
        if "tree_result" in self.sample_data:
            scores["tree_quality"] = self._analyze_tree_structure(
                self.sample_data["tree_result"],
                config
            )
        
        # 4. 최종 품질 분석
        if "final_result" in self.sample_data:
            scores["final_quality"] = self._analyze_final_quality(
                self.sample_data["final_result"],
                self.sample_data.get("original_text", "")
            )
        
        # 5. 예상 비용 계산
        scores["estimated_cost"] = self._calculate_estimated_cost(config)
        
        # 종합 점수
        scores["overall"] = self._calculate_overall_score(scores, config)
        
        return scores
    
    def _analyze_split_quality(self, split_data: Dict, config: TreeLLMConfig) -> float:
        """Split 품질 평가"""
        if isinstance(split_data, dict):
            sections = [v for v in split_data.values() if v]
        else:
            sections = split_data
        
        # 섹션 수 평가
        num_sections = len(sections)
        section_score = 1.0 if 5 <= num_sections <= 8 else 0.7
        
        # 섹션 길이 평가
        lengths = [len(str(s)) for s in sections]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        length_score = 1.0
        if avg_length < config.split.min_section_length:
            length_score = 0.5
        elif avg_length > config.split.max_section_length:
            length_score = 0.7
        
        return (section_score + length_score) / 2
    
    def _estimate_token_usage(self, build_output: str, config: TreeLLMConfig) -> float:
        """토큰 사용량 추정 및 효율성 평가"""
        # 대략적인 토큰 수 추정 (한글은 2-3토큰, 영어는 0.75토큰)
        korean_chars = sum(1 for c in build_output if '가' <= c <= '힣')
        english_chars = len(build_output) - korean_chars
        
        estimated_tokens = (korean_chars * 2.5) + (english_chars * 0.75)
        
        # 효율성 점수 (설정된 max_tokens 대비)
        efficiency = 1.0 - (estimated_tokens / config.model.max_tokens)
        
        return max(0, min(1, efficiency))
    
    def _analyze_tree_structure(self, tree_data: Dict, config: TreeLLMConfig) -> float:
        """트리 구조 품질 평가"""
        def get_depth(node, current_depth=0):
            if not isinstance(node, dict):
                return current_depth
            
            max_child_depth = current_depth
            for key, value in node.items():
                if isinstance(value, dict):
                    child_depth = get_depth(value, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            child_depth = get_depth(item, current_depth + 1)
                            max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        depth = get_depth(tree_data)
        
        # 적절한 깊이 평가
        if config.fuse.max_tree_depth - 1 <= depth <= config.fuse.max_tree_depth + 1:
            depth_score = 1.0
        else:
            depth_score = 0.7
        
        # 노드 수 평가 (간단히)
        node_count = str(tree_data).count('{')
        node_score = 1.0 if 10 <= node_count <= 50 else 0.7
        
        return (depth_score + node_score) / 2
    
    def _analyze_final_quality(self, final_text: str, original_text: str) -> float:
        """최종 출력 품질 평가"""
        # 길이 비율
        if original_text:
            length_ratio = len(final_text) / len(original_text)
            length_score = 1.0 if 0.8 <= length_ratio <= 1.5 else 0.7
        else:
            length_score = 0.8
        
        # 구조 완성도 (섹션 마커 확인)
        sections = ["Abstract", "Introduction", "Method", "Result", "Discussion", "Conclusion"]
        found_sections = sum(1 for s in sections if s.lower() in final_text.lower())
        structure_score = found_sections / len(sections)
        
        return (length_score + structure_score) / 2
    
    def _calculate_estimated_cost(self, config: TreeLLMConfig) -> float:
        """예상 API 비용 계산 (달러)"""
        # 추정 토큰 수
        input_tokens = 5000  # 평균적인 논문
        output_tokens = config.model.max_tokens
        
        # 모델별 가격 (추정)
        if config.model.model_name == "gpt-4o":
            cost_per_1k_input = 0.03
            cost_per_1k_output = 0.06
        elif config.model.model_name == "gpt-3.5-turbo":
            cost_per_1k_input = 0.001
            cost_per_1k_output = 0.002
        else:
            cost_per_1k_input = 0.01
            cost_per_1k_output = 0.03
        
        # 7개 프롬프트 (fill prompts) 실행
        total_cost = 7 * (
            (input_tokens / 1000 * cost_per_1k_input) +
            (output_tokens / 1000 * cost_per_1k_output)
        )
        
        return total_cost
    
    def _calculate_overall_score(self, scores: Dict[str, float], config: TreeLLMConfig) -> float:
        """종합 점수 계산"""
        # 가중치
        weights = {
            "split_quality": 0.15,
            "token_efficiency": 0.20,
            "tree_quality": 0.15,
            "final_quality": 0.30,
            "cost_efficiency": 0.20
        }
        
        # 비용 효율성 점수
        if "estimated_cost" in scores:
            scores["cost_efficiency"] = 1.0 / (1.0 + scores["estimated_cost"])
        
        total_score = 0
        total_weight = 0
        
        for key, weight in weights.items():
            if key in scores:
                total_score += scores[key] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def compare_presets(self) -> Dict[str, Dict]:
        """모든 프리셋 비교"""
        results = {}
        
        print("\n프리셋별 성능 분석")
        print("=" * 60)
        
        for preset_name in ["fast", "balanced", "thorough", "research"]:
            config = load_config(preset_name)
            scores = self.analyze_with_config(config)
            results[preset_name] = scores
            
            print(f"\n[{preset_name.upper()}]")
            print(f"  종합 점수: {scores['overall']:.3f}")
            print(f"  예상 비용: ${scores['estimated_cost']:.3f}")
            print(f"  품질 점수: {scores.get('final_quality', 0):.3f}")
            print(f"  효율성: {scores.get('token_efficiency', 0):.3f}")
        
        return results
    
    def find_optimal_params(self) -> Dict[str, any]:
        """최적 파라미터 조합 찾기"""
        best_score = 0
        best_config = None
        best_params = {}
        
        # 테스트할 파라미터 범위
        test_ranges = {
            "temperature": [0.1, 0.2, 0.3, 0.4, 0.5],
            "max_tokens": [1024, 2048, 3072, 4096],
            "top_p": [0.1, 0.3, 0.5, 0.7]
        }
        
        print("\n파라미터 최적화 진행 중...")
        
        # 기본 설정에서 시작
        base_config = load_config("balanced")
        
        # 각 파라미터별로 최적값 찾기
        for param_name, values in test_ranges.items():
            param_scores = []
            
            for value in values:
                # 설정 업데이트
                test_config = load_config("balanced")
                setattr(test_config.model, param_name, value)
                
                # 평가
                scores = self.analyze_with_config(test_config)
                param_scores.append((value, scores["overall"]))
                
                if scores["overall"] > best_score:
                    best_score = scores["overall"]
                    best_params[param_name] = value
            
            # 최적값 출력
            best_value = max(param_scores, key=lambda x: x[1])
            print(f"  {param_name}: {best_value[0]} (점수: {best_value[1]:.3f})")
        
        print(f"\n최적 조합 점수: {best_score:.3f}")
        return best_params


def run_efficient_test():
    """효율적인 테스트 실행"""
    tester = EfficientTester()
    
    # 1. 기존 데이터 확인
    print("로드된 샘플 데이터:")
    for key in tester.sample_data.keys():
        print(f"  - {key}")
    
    # 2. 프리셋 비교
    preset_results = tester.compare_presets()
    
    # 3. 최적 파라미터 찾기
    optimal_params = tester.find_optimal_params()
    
    # 4. 결과 저장
    results = {
        "preset_comparison": preset_results,
        "optimal_parameters": optimal_params,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    result_file = Path("hyperparameter_tests") / f"efficient_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
    result_file.parent.mkdir(exist_ok=True)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n결과 저장: {result_file}")
    
    # 5. 권장 설정 출력
    print("\n\n권장 하이퍼파라미터 설정:")
    print("=" * 40)
    print("config = TreeLLMConfig(")
    print("    model=ModelConfig(")
    for param, value in optimal_params.items():
        print(f"        {param}={value},")
    print("    )")
    print(")")


if __name__ == "__main__":
    run_efficient_test()
