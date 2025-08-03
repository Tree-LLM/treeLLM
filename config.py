"""
TreeLLM 하이퍼파라미터 구성 파일
─────────────────────────────────
논문 분석 LLM 서비스의 성능을 최적화하기 위한 세밀한 파라미터 설정
"""

from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """언어 모델 관련 설정"""
    model_name: str = "gpt-4o"
    temperature: float = 0.3  # 0.0 ~ 1.0, 낮을수록 일관된 출력
    top_p: float = 0.3  # 0.0 ~ 1.0, nucleus sampling
    max_tokens: int = 4096  # 최대 출력 토큰 수
    frequency_penalty: float = 0.0  # -2.0 ~ 2.0, 반복 단어 억제
    presence_penalty: float = 0.0  # -2.0 ~ 2.0, 새로운 주제 장려
    
    # 모델별 특화 설정
    model_specific_params: Dict[str, Any] = field(default_factory=lambda: {
        "gpt-4o": {
            "temperature": 0.3,
            "top_p": 0.3,
            "max_tokens": 4096
        },
        "gpt-4": {
            "temperature": 0.4,
            "top_p": 0.4,
            "max_tokens": 8192
        },
        "gpt-3.5-turbo": {
            "temperature": 0.5,
            "top_p": 0.5,
            "max_tokens": 4096
        }
    })


@dataclass
class SplitConfig:
    """문서 분할 관련 설정"""
    valid_sections: set = field(default_factory=lambda: {
        "Abstract", "Introduction", "Related Work", 
        "Background", "Method", "Discussion", "Conclusion"
    })
    min_section_length: int = 50  # 섹션 최소 글자 수
    max_section_length: int = 10000  # 섹션 최대 글자 수
    merge_short_sections: bool = True  # 짧은 섹션 병합 여부
    heading_confidence_threshold: float = 0.8  # 제목 인식 신뢰도 임계값


@dataclass
class BuildConfig:
    """Build 단계 설정"""
    parallel_processing: bool = True  # 병렬 처리 여부
    max_workers: int = 3  # 동시 작업 수
    retry_attempts: int = 3  # API 호출 재시도 횟수
    retry_delay: float = 1.0  # 재시도 대기 시간(초)
    timeout: float = 60.0  # API 호출 타임아웃(초)
    
    # 프롬프트별 세부 설정
    prompt_specific_params: Dict[str, Any] = field(default_factory=lambda: {
        "critical_analysis": {
            "temperature": 0.4,
            "max_tokens": 2048
        },
        "methodology_review": {
            "temperature": 0.3,
            "max_tokens": 3072
        },
        "contribution_assessment": {
            "temperature": 0.5,
            "max_tokens": 2048
        }
    })


@dataclass
class FuseConfig:
    """Tree 구조 생성 관련 설정"""
    max_tree_depth: int = 5  # 최대 트리 깊이
    min_node_content_length: int = 20  # 노드 최소 내용 길이
    similarity_threshold: float = 0.7  # 노드 병합 유사도 임계값
    balance_factor: float = 0.8  # 트리 균형 계수
    
    # 트리 구조 최적화 설정
    optimization_params: Dict[str, Any] = field(default_factory=lambda: {
        "enable_pruning": True,  # 불필요한 노드 제거
        "enable_merging": True,  # 유사 노드 병합
        "enable_rebalancing": True  # 트리 재균형
    })


@dataclass
class AuditConfig:
    """감사 단계 설정"""
    strictness_level: str = "medium"  # low, medium, high
    check_categories: list = field(default_factory=lambda: [
        "logical_consistency",
        "evidence_support",
        "methodology_rigor",
        "result_validity",
        "citation_accuracy"
    ])
    score_threshold: float = 0.7  # 통과 기준 점수
    detailed_feedback: bool = True  # 상세 피드백 제공 여부


@dataclass
class EditConfig:
    """편집 단계 설정"""
    # EditPass1 설정
    edit1_params: Dict[str, Any] = field(default_factory=lambda: {
        "focus_areas": ["clarity", "coherence", "flow"],
        "preservation_ratio": 0.8,  # 원본 보존 비율
        "enhancement_level": "moderate"  # minimal, moderate, extensive
    })
    
    # EditPass2 설정
    edit2_params: Dict[str, Any] = field(default_factory=lambda: {
        "global_consistency_check": True,
        "terminology_standardization": True,
        "reference_validation": True,
        "final_polish_level": "high"
    })


@dataclass
class GlobalCheckConfig:
    """전역 검사 설정"""
    check_items: list = field(default_factory=lambda: [
        "overall_coherence",
        "argument_flow",
        "evidence_completeness",
        "conclusion_alignment",
        "abstract_accuracy"
    ])
    coherence_threshold: float = 0.75
    require_all_checks: bool = False  # 모든 검사 통과 필수 여부


@dataclass
class OutputConfig:
    """출력 관련 설정"""
    output_format: str = "markdown"  # markdown, latex, html
    include_metadata: bool = True  # 메타데이터 포함 여부
    include_confidence_scores: bool = True  # 신뢰도 점수 포함
    generate_summary: bool = True  # 요약 생성 여부
    summary_length: int = 500  # 요약 길이(단어)


@dataclass
class TreeLLMConfig:
    """TreeLLM 전체 구성"""
    model: ModelConfig = field(default_factory=ModelConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    build: BuildConfig = field(default_factory=BuildConfig)
    fuse: FuseConfig = field(default_factory=FuseConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    edit: EditConfig = field(default_factory=EditConfig)
    global_check: GlobalCheckConfig = field(default_factory=GlobalCheckConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # 전역 설정
    debug_mode: bool = False
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    save_intermediate_results: bool = True
    result_dir: str = "sample"
    
    def get_model_params(self, model_name: str = None) -> Dict[str, Any]:
        """특정 모델의 파라미터 반환"""
        model_name = model_name or self.model.model_name
        if model_name in self.model.model_specific_params:
            return self.model.model_specific_params[model_name]
        return {
            "temperature": self.model.temperature,
            "top_p": self.model.top_p,
            "max_tokens": self.model.max_tokens
        }
    
    def get_prompt_params(self, prompt_type: str) -> Dict[str, Any]:
        """특정 프롬프트의 파라미터 반환"""
        base_params = self.get_model_params()
        if prompt_type in self.build.prompt_specific_params:
            base_params.update(self.build.prompt_specific_params[prompt_type])
        return base_params
    
    def validate(self) -> bool:
        """설정 유효성 검증"""
        # Temperature 범위 확인
        if not 0 <= self.model.temperature <= 1:
            raise ValueError(f"Temperature must be between 0 and 1, got {self.model.temperature}")
        
        # Top-p 범위 확인
        if not 0 <= self.model.top_p <= 1:
            raise ValueError(f"Top-p must be between 0 and 1, got {self.model.top_p}")
        
        # 임계값 범위 확인
        thresholds = [
            self.split.heading_confidence_threshold,
            self.fuse.similarity_threshold,
            self.audit.score_threshold,
            self.global_check.coherence_threshold
        ]
        for threshold in thresholds:
            if not 0 <= threshold <= 1:
                raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
        
        return True


# 사전 정의된 구성 프리셋
PRESETS = {
    "fast": TreeLLMConfig(
        model=ModelConfig(temperature=0.5, top_p=0.5),
        build=BuildConfig(parallel_processing=True, max_workers=5),
        audit=AuditConfig(strictness_level="low"),
        edit=EditConfig(
            edit1_params={"enhancement_level": "minimal"},
            edit2_params={"final_polish_level": "moderate"}
        )
    ),
    
    "balanced": TreeLLMConfig(),  # 기본값 사용
    
    "thorough": TreeLLMConfig(
        model=ModelConfig(temperature=0.2, top_p=0.2),
        build=BuildConfig(parallel_processing=True, max_workers=2),
        audit=AuditConfig(strictness_level="high", detailed_feedback=True),
        edit=EditConfig(
            edit1_params={"enhancement_level": "extensive"},
            edit2_params={"final_polish_level": "high"}
        ),
        global_check=GlobalCheckConfig(require_all_checks=True)
    ),
    
    "research": TreeLLMConfig(
        model=ModelConfig(temperature=0.1, top_p=0.1, max_tokens=8192),
        split=SplitConfig(min_section_length=100),
        audit=AuditConfig(
            strictness_level="high",
            check_categories=[
                "logical_consistency",
                "evidence_support",
                "methodology_rigor",
                "result_validity",
                "citation_accuracy",
                "statistical_validity",
                "reproducibility"
            ]
        ),
        output=OutputConfig(
            include_confidence_scores=True,
            generate_summary=True,
            summary_length=1000
        )
    )
}


def load_config(preset: str = "balanced", **overrides) -> TreeLLMConfig:
    """프리셋 로드 및 커스터마이징"""
    if preset not in PRESETS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(PRESETS.keys())}")
    
    config = PRESETS[preset]
    
    # 오버라이드 적용
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    config.validate()
    return config


if __name__ == "__main__":
    # 설정 테스트
    config = load_config("balanced")
    print("기본 설정:", config.model)
    
    # 커스텀 설정
    custom_config = load_config(
        "thorough",
        model=ModelConfig(temperature=0.15),
        debug_mode=True
    )
    print("\n커스텀 설정:", custom_config.model)
    
    # 모델별 파라미터 확인
    print("\nGPT-4o 파라미터:", config.get_model_params("gpt-4o"))
    print("Critical Analysis 파라미터:", config.get_prompt_params("critical_analysis"))
