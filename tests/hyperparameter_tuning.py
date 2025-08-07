"""
TreeLLM 하이퍼파라미터 튜닝 가이드
═══════════════════════════════════
OpenAI API 비용을 최소화하면서 최적의 성능을 찾기 위한 전략
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json
import time
from pathlib import Path
import numpy as np
from config import TreeLLMConfig, load_config


@dataclass
class HyperparameterRange:
    """하이퍼파라미터 범위 정의"""
    
    # LLM 관련 파라미터
    TEMPERATURE = {
        "default": 0.3,
        "range": [0.0, 1.0],
        "optimal_range": [0.1, 0.5],
        "step": 0.1,
        "description": "창의성 vs 일관성 제어. 논문 분석에는 낮은 값 권장"
    }
    
    TOP_P = {
        "default": 0.3,
        "range": [0.0, 1.0],
        "optimal_range": [0.1, 0.5],
        "step": 0.1,
        "description": "Nucleus sampling. Temperature와 함께 사용"
    }
    
    MAX_TOKENS = {
        "default": 4096,
        "range": [500, 8192],
        "optimal_range": [2048, 4096],
        "step": 512,
        "description": "출력 길이 제한. 비용과 직결"
    }
    
    FREQUENCY_PENALTY = {
        "default": 0.0,
        "range": [-2.0, 2.0],
        "optimal_range": [0.0, 0.5],
        "step": 0.1,
        "description": "반복 단어 억제. 논문에는 낮은 값 사용"
    }
    
    PRESENCE_PENALTY = {
        "default": 0.0,
        "range": [-2.0, 2.0],
        "optimal_range": [0.0, 0.3],
        "step": 0.1,
        "description": "새로운 주제 장려. 논문에는 낮은 값 사용"
    }
    
    # 시스템 관련 파라미터
    BATCH_SIZE = {
        "default": 3,
        "range": [1, 10],
        "optimal_range": [2, 5],
        "step": 1,
        "description": "병렬 처리 작업 수. 메모리와 속도 균형"
    }
    
    RETRY_ATTEMPTS = {
        "default": 3,
        "range": [1, 5],
        "optimal_range": [2, 3],
        "step": 1,
        "description": "API 호출 재시도 횟수"
    }
    
    TIMEOUT = {
        "default": 60.0,
        "range": [30.0, 180.0],
        "optimal_range": [45.0, 90.0],
        "step": 15.0,
        "description": "API 호출 타임아웃 (초)"
    }
    
    # 문서 처리 파라미터
    MIN_SECTION_LENGTH = {
        "default": 50,
        "range": [10, 200],
        "optimal_range": [30, 100],
        "step": 10,
        "description": "섹션 최소 길이. 너무 짧은 섹션 제거"
    }
    
    MAX_SECTION_LENGTH = {
        "default": 10000,
        "range": [5000, 20000],
        "optimal_range": [8000, 12000],
        "step": 1000,
        "description": "섹션 최대 길이. 메모리 관리"
    }
    
    # 트리 구조 파라미터
    MAX_TREE_DEPTH = {
        "default": 5,
        "range": [3, 10],
        "optimal_range": [4, 6],
        "step": 1,
        "description": "트리 최대 깊이. 구조 복잡도"
    }
    
    MIN_NODE_CONTENT_LENGTH = {
        "default": 20,
        "range": [10, 50],
        "optimal_range": [15, 30],
        "step": 5,
        "description": "노드 최소 내용 길이"
    }
    
    SIMILARITY_THRESHOLD = {
        "default": 0.7,
        "range": [0.5, 0.9],
        "optimal_range": [0.65, 0.75],
        "step": 0.05,
        "description": "노드 병합 유사도 임계값"
    }


class LocalTester:
    """로컬 테스트를 위한 도구"""
    
    def __init__(self, base_config: TreeLLMConfig = None):
        self.base_config = base_config or load_config("balanced")
        self.test_results = []
        self.test_dir = Path("hyperparameter_tests")
        self.test_dir.mkdir(exist_ok=True)
    
    def create_test_config(self, **params) -> TreeLLMConfig:
        """테스트용 설정 생성"""
        config = load_config("balanced")
        
        # 파라미터 적용
        for key, value in params.items():
            if hasattr(config.model, key):
                setattr(config.model, key, value)
            elif hasattr(config.build, key):
                setattr(config.build, key, value)
            elif hasattr(config.split, key):
                setattr(config.split, key, value)
            elif hasattr(config.fuse, key):
                setattr(config.fuse, key, value)
        
        return config
    
    def simulate_api_call(self, prompt: str, config: TreeLLMConfig) -> Dict:
        """API 호출 시뮬레이션 (실제 호출 없이)"""
        # 파라미터에 따른 예상 결과 시뮬레이션
        base_quality = 0.7
        
        # Temperature 영향
        if config.model.temperature < 0.3:
            base_quality += 0.1  # 일관성 증가
        elif config.model.temperature > 0.7:
            base_quality -= 0.1  # 일관성 감소
        
        # Max tokens 영향
        if config.model.max_tokens < 2048:
            base_quality -= 0.05  # 내용 부족 가능성
        
        # 예상 비용 계산
        estimated_cost = self._estimate_cost(prompt, config)
        
        # 예상 처리 시간
        estimated_time = len(prompt) / 1000 * config.model.max_tokens / 1000
        
        return {
            "quality_score": base_quality,
            "estimated_cost": estimated_cost,
            "estimated_time": estimated_time,
            "consistency": 1.0 - config.model.temperature,
            "completeness": min(1.0, config.model.max_tokens / 4096)
        }
    
    def _estimate_cost(self, prompt: str, config: TreeLLMConfig) -> float:
        """비용 추정 (달러)"""
        # GPT-4 기준 추정 (실제 가격과 다를 수 있음)
        input_tokens = len(prompt) / 4  # 대략적인 토큰 수
        output_tokens = config.model.max_tokens
        
        if config.model.model_name == "gpt-4o":
            input_cost = input_tokens * 0.03 / 1000
            output_cost = output_tokens * 0.06 / 1000
        elif config.model.model_name == "gpt-3.5-turbo":
            input_cost = input_tokens * 0.001 / 1000
            output_cost = output_tokens * 0.002 / 1000
        else:
            input_cost = input_tokens * 0.01 / 1000
            output_cost = output_tokens * 0.03 / 1000
        
        return input_cost + output_cost
    
    def test_parameter_combination(self, params: Dict, test_text: str) -> Dict:
        """특정 파라미터 조합 테스트"""
        config = self.create_test_config(**params)
        
        # 각 단계별 시뮬레이션
        results = {
            "parameters": params,
            "scores": {},
            "metrics": {}
        }
        
        # Split 단계 테스트
        split_score = self._test_split(test_text, config)
        results["scores"]["split"] = split_score
        
        # Build 단계 시뮬레이션
        build_result = self.simulate_api_call(test_text, config)
        results["scores"]["build"] = build_result["quality_score"]
        results["metrics"]["estimated_cost"] = build_result["estimated_cost"]
        results["metrics"]["estimated_time"] = build_result["estimated_time"]
        
        # 전체 점수 계산
        results["overall_score"] = self._calculate_overall_score(results)
        
        return results
    
    def _test_split(self, text: str, config: TreeLLMConfig) -> float:
        """Split 단계 테스트"""
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            if line.strip() and len(line.strip()) > 10:
                current_section.append(line)
            elif current_section:
                section_text = ' '.join(current_section)
                if len(section_text) >= config.split.min_section_length:
                    sections.append(section_text)
                current_section = []
        
        # 섹션 품질 평가
        if not sections:
            return 0.0
        
        avg_length = sum(len(s) for s in sections) / len(sections)
        optimal_length = (config.split.min_section_length + config.split.max_section_length) / 2
        
        length_score = 1.0 - abs(avg_length - optimal_length) / optimal_length
        count_score = min(1.0, len(sections) / 7)  # 7개 섹션이 이상적
        
        return (length_score + count_score) / 2
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """전체 점수 계산"""
        scores = results["scores"]
        metrics = results["metrics"]
        
        # 품질 점수 (60%)
        quality_score = np.mean(list(scores.values()))
        
        # 비용 효율성 (30%)
        cost_efficiency = 1.0 / (1.0 + metrics["estimated_cost"])
        
        # 시간 효율성 (10%)
        time_efficiency = 1.0 / (1.0 + metrics["estimated_time"])
        
        return 0.6 * quality_score + 0.3 * cost_efficiency + 0.1 * time_efficiency
    
    def grid_search(self, param_ranges: Dict, test_text: str, max_tests: int = 50) -> List[Dict]:
        """그리드 서치 (제한된 횟수)"""
        # 파라미터 조합 생성
        param_combinations = self._generate_combinations(param_ranges, max_tests)
        
        results = []
        for i, params in enumerate(param_combinations):
            print(f"Testing combination {i+1}/{len(param_combinations)}")
            result = self.test_parameter_combination(params, test_text)
            results.append(result)
            
            # 중간 결과 저장
            if i % 10 == 0:
                self._save_intermediate_results(results)
        
        # 최종 결과 저장
        self._save_final_results(results)
        
        return sorted(results, key=lambda x: x["overall_score"], reverse=True)
    
    def _generate_combinations(self, param_ranges: Dict, max_tests: int) -> List[Dict]:
        """파라미터 조합 생성 (스마트 샘플링)"""
        # 중요 파라미터 우선 순위
        priority_params = ["temperature", "max_tokens", "top_p"]
        
        combinations = []
        
        # 1. 기본값 조합
        base_params = {k: v["default"] for k, v in param_ranges.items()}
        combinations.append(base_params.copy())
        
        # 2. 각 파라미터별 최적 범위 테스트
        for param, info in param_ranges.items():
            if param in priority_params:
                for value in np.linspace(info["optimal_range"][0], 
                                       info["optimal_range"][1], 
                                       5):
                    test_params = base_params.copy()
                    test_params[param] = value
                    combinations.append(test_params)
        
        # 3. 랜덤 조합 추가
        while len(combinations) < max_tests:
            random_params = {}
            for param, info in param_ranges.items():
                if np.random.random() < 0.3:  # 30% 확률로 변경
                    random_params[param] = np.random.uniform(
                        info["optimal_range"][0],
                        info["optimal_range"][1]
                    )
                else:
                    random_params[param] = info["default"]
            combinations.append(random_params)
        
        return combinations[:max_tests]
    
    def _save_intermediate_results(self, results: List[Dict]):
        """중간 결과 저장"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filepath = self.test_dir / f"intermediate_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def _save_final_results(self, results: List[Dict]):
        """최종 결과 저장"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # 상위 10개 결과
        top_results = sorted(results, key=lambda x: x["overall_score"], reverse=True)[:10]
        
        # JSON 저장
        filepath = self.test_dir / f"final_results_{timestamp}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "top_10": top_results,
                "total_tested": len(results),
                "best_params": top_results[0]["parameters"],
                "best_score": top_results[0]["overall_score"]
            }, f, indent=2, ensure_ascii=False)
        
        # 읽기 쉬운 보고서 생성
        report_path = self.test_dir / f"report_{timestamp}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("TreeLLM 하이퍼파라미터 튜닝 결과\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("최적 파라미터 조합:\n")
            f.write("-" * 30 + "\n")
            for param, value in top_results[0]["parameters"].items():
                f.write(f"{param}: {value}\n")
            
            f.write(f"\n전체 점수: {top_results[0]['overall_score']:.4f}\n")
            f.write(f"예상 비용: ${top_results[0]['metrics']['estimated_cost']:.4f}\n")
            f.write(f"예상 시간: {top_results[0]['metrics']['estimated_time']:.2f}초\n")
        
        print(f"\n결과 저장 완료: {filepath}")
        print(f"보고서 저장 완료: {report_path}")


# 하이퍼파라미터 조정 전략
class TuningStrategy:
    """단계별 하이퍼파라미터 조정 전략"""
    
    @staticmethod
    def get_tuning_sequence() -> List[Tuple[str, str]]:
        """조정 순서 반환"""
        return [
            # 1단계: 핵심 LLM 파라미터
            ("temperature", "품질과 일관성의 기본 균형 설정"),
            ("max_tokens", "비용과 완성도 균형 설정"),
            
            # 2단계: 샘플링 파라미터
            ("top_p", "Temperature와 함께 미세 조정"),
            ("frequency_penalty", "반복 제어"),
            
            # 3단계: 시스템 파라미터
            ("batch_size", "처리 속도 최적화"),
            ("retry_attempts", "안정성 확보"),
            
            # 4단계: 문서 처리 파라미터
            ("min_section_length", "섹션 품질 확보"),
            ("max_tree_depth", "구조 복잡도 조정")
        ]
    
    @staticmethod
    def get_evaluation_metrics() -> Dict[str, str]:
        """평가 지표"""
        return {
            "quality_score": "출력 품질 (일관성, 완성도, 정확성)",
            "cost_efficiency": "API 비용 대비 품질",
            "time_efficiency": "처리 시간 대비 품질",
            "consistency_score": "섹션 간 일관성",
            "completeness_score": "정보 완성도",
            "structure_score": "문서 구조 품질"
        }


# 테스트 실행 함수
def run_hyperparameter_tuning(test_file: str = "sample/example.txt"):
    """하이퍼파라미터 튜닝 실행"""
    
    print("TreeLLM 하이퍼파라미터 튜닝 시작")
    print("=" * 50)
    
    # 테스트 텍스트 로드
    if Path(test_file).exists():
        test_text = Path(test_file).read_text(encoding='utf-8')
    else:
        # 샘플 텍스트 생성
        test_text = """
        # Introduction
        This paper presents a novel approach to natural language processing.
        We propose a new method that significantly improves performance.
        
        # Method
        Our approach consists of three main components.
        First, we preprocess the data. Second, we apply our algorithm.
        Finally, we evaluate the results.
        
        # Results
        Our experiments show significant improvements over baselines.
        The proposed method achieves state-of-the-art performance.
        
        # Conclusion
        We have presented a new approach that advances the field.
        Future work will explore additional applications.
        """
    
    # 로컬 테스터 초기화
    tester = LocalTester()
    
    # 테스트할 파라미터 범위 정의
    param_ranges = {
        "temperature": HyperparameterRange.TEMPERATURE,
        "max_tokens": HyperparameterRange.MAX_TOKENS,
        "top_p": HyperparameterRange.TOP_P,
        "batch_size": HyperparameterRange.BATCH_SIZE
    }
    
    # 1. 빠른 테스트 (20개 조합)
    print("\n1. 빠른 파라미터 스캔 (20개 조합)")
    quick_results = tester.grid_search(param_ranges, test_text, max_tests=20)
    
    print(f"\n최적 파라미터 (빠른 스캔):")
    print(f"점수: {quick_results[0]['overall_score']:.4f}")
    for param, value in quick_results[0]["parameters"].items():
        print(f"  {param}: {value}")
    
    # 2. 상세 테스트 (최적 영역 중심)
    print("\n2. 상세 파라미터 튜닝 (최적 영역 중심)")
    
    # 최적 영역 정의
    best_params = quick_results[0]["parameters"]
    refined_ranges = {}
    
    for param, value in best_params.items():
        if param in param_ranges:
            # 최적값 주변 ±20% 범위로 상세 탐색
            original_range = param_ranges[param]["optimal_range"]
            range_size = original_range[1] - original_range[0]
            refined_ranges[param] = {
                "default": value,
                "optimal_range": [
                    max(original_range[0], value - range_size * 0.2),
                    min(original_range[1], value + range_size * 0.2)
                ]
            }
    
    # 상세 테스트 실행
    detailed_results = tester.grid_search(refined_ranges, test_text, max_tests=30)
    
    print(f"\n최종 최적 파라미터:")
    print(f"점수: {detailed_results[0]['overall_score']:.4f}")
    print(f"예상 비용: ${detailed_results[0]['metrics']['estimated_cost']:.4f}")
    for param, value in detailed_results[0]["parameters"].items():
        print(f"  {param}: {value:.3f}")
    
    return detailed_results[0]


if __name__ == "__main__":
    # 하이퍼파라미터 튜닝 실행
    best_config = run_hyperparameter_tuning()
    
    print("\n" + "=" * 50)
    print("튜닝 완료!")
    print(f"결과는 ./hyperparameter_tests/ 디렉토리에 저장되었습니다.")
    
    print("\n권장 설정 (config.py에 적용):")
    print("-" * 30)
    print("config = TreeLLMConfig(")
    print("    model=ModelConfig(")
    for param, value in best_config["parameters"].items():
        if param in ["temperature", "max_tokens", "top_p"]:
            print(f"        {param}={value:.3f},")
    print("    ),")
    print("    build=BuildConfig(")
    for param, value in best_config["parameters"].items():
        if param in ["batch_size", "retry_attempts"]:
            print(f"        {param}={int(value)},")
    print("    )")
    print(")")
