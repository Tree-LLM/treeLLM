"""
Enhanced Orchestrator V3 - Optimized Hyperparameter Implementation
─────────────────────────────────────────────────────────────────
TreeLLM Pipeline with Stage-Specific Optimization and Advanced Testing
"""

from pathlib import Path
import json
from datetime import datetime
import os
import time
from typing import Dict, Any, Optional, Generator, List
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys
import hashlib
sys.path.append(str(Path(__file__).parent.parent))

# 설정 및 모듈 임포트
from config import TreeLLMConfig, load_config, ModelConfig
from module.build import BuildStep
from module.split import run as split_run
from module.fuse import TreeBuilder
from module.audit import AuditStep
from module.edit_pass1 import EditPass1
from module.global_check import GlobalCheck
from module.edit_pass2 import EditPass2


class QualityMetrics:
    """Quality metrics tracking for pipeline optimization"""
    
    def __init__(self):
        self.metrics = {
            "accuracy": {
                "factual_correctness": 0.0,
                "quote_accuracy": 0.0,
                "structure_preservation": 0.0
            },
            "completeness": {
                "section_coverage": 0.0,
                "detail_depth": 0.0,
                "citation_capture": 0.0
            },
            "consistency": {
                "cross_section_alignment": 0.0,
                "terminology_consistency": 0.0,
                "format_adherence": 0.0
            },
            "efficiency": {
                "processing_time": 0.0,
                "token_usage": 0,
                "api_calls": 0,
                "cost_estimate": 0.0
            }
        }
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall quality score"""
        accuracy_score = sum(self.metrics["accuracy"].values()) / 3
        completeness_score = sum(self.metrics["completeness"].values()) / 3
        consistency_score = sum(self.metrics["consistency"].values()) / 3
        
        # Weighted average (accuracy is most important for academic papers)
        return (accuracy_score * 0.4 + 
                completeness_score * 0.35 + 
                consistency_score * 0.25)
    
    def update_from_stage(self, stage_name: str, stage_output: Any):
        """Update metrics based on stage output"""
        if stage_name == "split":
            self._update_split_metrics(stage_output)
        elif stage_name == "build":
            self._update_build_metrics(stage_output)
        elif stage_name == "audit":
            self._update_audit_metrics(stage_output)
    
    def _update_split_metrics(self, output):
        """Update metrics from split stage"""
        if output and isinstance(output, dict):
            self.metrics["completeness"]["section_coverage"] = min(len(output) / 7, 1.0)
    
    def _update_build_metrics(self, output):
        """Update metrics from build stage"""
        if output and isinstance(output, dict):
            # Check for quotes and evidence
            quote_count = str(output).count('"')
            self.metrics["accuracy"]["quote_accuracy"] = min(quote_count / 20, 1.0)
    
    def _update_audit_metrics(self, output):
        """Update metrics from audit stage"""
        if output and isinstance(output, dict):
            # Extract quality scores from audit
            if "quality_score" in output:
                self.metrics["accuracy"]["factual_correctness"] = output["quality_score"]


class EnhancedOrchestratorV3:
    """Enhanced Orchestrator with optimized hyperparameters and quality tracking"""
    
    # Preset configurations optimized for different use cases
    PRESETS = {
        "fast": {
            "name": "Fast Processing",
            "description": "Quick draft analysis",
            "model": "gpt-3.5-turbo",
            "base_temperature": 0.4,
            "workers": 5
        },
        "balanced": {
            "name": "Balanced",
            "description": "Default balanced processing",
            "model": "gpt-4o",
            "base_temperature": 0.2,
            "workers": 3
        },
        "precision": {
            "name": "High Precision",
            "description": "Publication quality analysis",
            "model": "gpt-4o",
            "base_temperature": 0.1,
            "workers": 2
        },
        "research": {
            "name": "Research Grade",
            "description": "Maximum quality for research",
            "model": "gpt-4o",
            "base_temperature": 0.05,
            "workers": 1
        }
    }
    
    def __init__(self, config: TreeLLMConfig = None, preset: str = "balanced", 
                 enable_metrics: bool = True, enable_caching: bool = True):
        """
        Initialize Enhanced Orchestrator
        
        Args:
            config: TreeLLMConfig instance
            preset: Preset configuration name
            enable_metrics: Enable quality metrics tracking
            enable_caching: Enable result caching
        """
        self.preset = preset
        self.config = config or self._load_optimized_config(preset)
        self.config.validate()
        
        # Enhanced features
        self.enable_metrics = enable_metrics
        self.enable_caching = enable_caching
        self.quality_metrics = QualityMetrics() if enable_metrics else None
        
        # Result directories
        self.base_dir = Path(self.config.result_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.base_dir / "cache"
        if enable_caching:
            self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_enhanced_logging()
        
        # Performance tracking
        self.performance_data = {
            "start_time": None,
            "end_time": None,
            "stage_metrics": {},
            "total_api_calls": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0
        }
    
    def _load_optimized_config(self, preset: str) -> TreeLLMConfig:
        """Load optimized configuration based on preset"""
        if preset not in self.PRESETS:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(self.PRESETS.keys())}")
        
        preset_config = self.PRESETS[preset]
        config = load_config(preset)
        
        # Apply preset-specific settings
        config.model.model_name = preset_config["model"]
        config.model.temperature = preset_config["base_temperature"]
        config.build.max_workers = preset_config["workers"]
        
        # Apply stage-specific parameters from ModelConfig
        if hasattr(config.model, 'stage_specific_params'):
            self.stage_params = config.model.stage_specific_params
        else:
            self.stage_params = {}
        
        return config
    
    def _setup_enhanced_logging(self):
        """Setup enhanced logging with multiple handlers"""
        log_level = getattr(logging, self.config.log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler for all logs
        file_handler = logging.FileHandler(self.base_dir / "orchestrator_enhanced.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # File handler for errors only
        error_handler = logging.FileHandler(self.base_dir / "errors.log")
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear existing handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log(self, message: str, level: str = "INFO", stage: str = None):
        """Enhanced logging with stage information"""
        if stage:
            message = f"[{stage}] {message}"
        getattr(self.logger, level.lower())(message)
    
    def _get_cache_key(self, stage: str, input_hash: str) -> str:
        """Generate cache key for stage results"""
        return f"{stage}_{input_hash}_{self.preset}"
    
    def _get_input_hash(self, text: str) -> str:
        """Generate hash for input text"""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    def _load_from_cache(self, cache_key: str) -> Optional[Any]:
        """Load cached result if available"""
        if not self.enable_caching:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            self.log(f"Loading from cache: {cache_key}", "DEBUG")
            return json.loads(cache_file.read_text(encoding="utf-8"))
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any):
        """Save result to cache"""
        if not self.enable_caching:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), 
            encoding="utf-8"
        )
        self.log(f"Saved to cache: {cache_key}", "DEBUG")
    
    def _save_intermediate(self, filename: str, content: Any):
        """Save intermediate results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.base_dir / f"{filename}_{timestamp}.json"
        
        if isinstance(content, str):
            content = {"content": content}
        
        filepath.write_text(
            json.dumps(content, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self.log(f"Saved intermediate: {filepath.name}", "DEBUG")
    
    def _save_final_result(self, result: Dict):
        """Save final pipeline result"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.base_dir / f"final_result_{self.preset}_{timestamp}.json"
        
        filepath.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        self.log(f"Saved final result: {filepath.name}", "INFO")
    
    def _run_split_stage(self, raw_text: str, input_hash: str) -> Dict:
        """Run split stage with optimized parameters"""
        stage_name = "split"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            self.log(f"Using optimized params: temp={params.get('temperature', 'default')}", 
                    "DEBUG", stage_name)
        
        try:
            result = split_run(raw_text)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.quality_metrics:
                self.quality_metrics.update_from_stage(stage_name, result)
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_build_stage(self, raw_text: str, input_hash: str) -> Dict:
        """Run build stage with optimized parameters"""
        stage_name = "build"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            # Update config for this stage
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.2)
            temp_config.model.top_p = params.get("top_p", 0.3)
            temp_config.model.max_tokens = params.get("max_tokens", 4096)
            
            self.log(f"Using optimized params: temp={params.get('temperature')}, "
                    f"top_p={params.get('top_p')}", "DEBUG", stage_name)
        
        try:
            # BuildStep doesn't take config parameter, it takes model name
            model_name = temp_config.model.model_name if 'temp_config' in locals() else self.config.model.model_name
            builder = BuildStep(model=model_name)
            result = builder.run(raw_text)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.quality_metrics:
                self.quality_metrics.update_from_stage(stage_name, result)
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_fuse_stage(self, build_result: Dict, input_hash: str) -> Dict:
        """Run fuse stage with optimized parameters"""
        stage_name = "fuse"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.15)
            temp_config.model.top_p = params.get("top_p", 0.2)
            temp_config.model.max_tokens = params.get("max_tokens", 6144)
        
        try:
            # TreeBuilder doesn't take config parameter
            tree_builder = TreeBuilder()
            result = tree_builder.run(build_result)
            result_dict = json.loads(result) if isinstance(result, str) else result
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result_dict)
            
            return result_dict
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_audit_stage(self, sections: Dict, tree: Dict, input_hash: str) -> Dict:
        """Run audit stage with optimized parameters"""
        stage_name = "audit"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters (very low temperature for accuracy)
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.05)
            temp_config.model.top_p = params.get("top_p", 0.1)
            temp_config.model.max_tokens = params.get("max_tokens", 3072)
        
        try:
            # AuditStep takes model name parameter
            model_name = temp_config.model.model_name if 'temp_config' in locals() else self.config.model.model_name
            auditor = AuditStep(model=model_name)
            result = auditor.run(sections, tree)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.quality_metrics:
                self.quality_metrics.update_from_stage(stage_name, result)
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_edit_pass1_stage(self, sections: Dict, tree: Dict, 
                              audit_result: Dict, input_hash: str) -> Dict:
        """Run first edit pass with optimized parameters"""
        stage_name = "edit_pass1"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.25)
            temp_config.model.top_p = params.get("top_p", 0.4)
            temp_config.model.max_tokens = params.get("max_tokens", 4096)
            temp_config.model.frequency_penalty = params.get("frequency_penalty", 0.2)
            temp_config.model.presence_penalty = params.get("presence_penalty", 0.1)
        
        try:
            # EditPass1 takes model name parameter
            model_name = temp_config.model.model_name if 'temp_config' in locals() else self.config.model.model_name
            editor = EditPass1(model=model_name)
            result = editor.run(sections, tree, audit_result)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_global_check_stage(self, edit1_result: Dict, input_hash: str) -> Dict:
        """Run global consistency check with optimized parameters"""
        stage_name = "global_check"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.1)
            temp_config.model.top_p = params.get("top_p", 0.2)
            temp_config.model.max_tokens = params.get("max_tokens", 3072)
        
        try:
            # GlobalCheck takes model name parameter
            model_name = temp_config.model.model_name if 'temp_config' in locals() else self.config.model.model_name
            checker = GlobalCheck(model=model_name)
            result = checker.run(edit1_result)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def _run_edit_pass2_stage(self, edit1_result: Dict, 
                              global_result: Dict, input_hash: str) -> Dict:
        """Run final edit pass with optimized parameters"""
        stage_name = "edit_pass2"
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(stage_name, input_hash)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        self.log(f"Starting {stage_name}", stage=stage_name)
        
        # Apply stage-specific parameters
        if stage_name in self.stage_params:
            params = self.stage_params[stage_name]
            temp_config = self.config
            temp_config.model.temperature = params.get("temperature", 0.2)
            temp_config.model.top_p = params.get("top_p", 0.3)
            temp_config.model.max_tokens = params.get("max_tokens", 4096)
            temp_config.model.frequency_penalty = params.get("frequency_penalty", 0.15)
            temp_config.model.presence_penalty = params.get("presence_penalty", 0.05)
        
        try:
            # EditPass2 takes model name parameter
            model_name = temp_config.model.model_name if 'temp_config' in locals() else self.config.model.model_name
            editor = EditPass2(model=model_name)
            result = editor.run(edit1_result, global_result)
            
            # Track metrics
            duration = time.time() - start_time
            self.performance_data["stage_metrics"][stage_name] = {
                "duration": duration,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log(f"Completed in {duration:.2f}s", stage=stage_name)
            
            # Cache result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            self.log(f"Failed: {e}", "ERROR", stage_name)
            raise
    
    def run(self, infile_text: str, save_intermediate: bool = True) -> Dict[str, Any]:
        """
        Run the enhanced pipeline with optimized parameters
        
        Args:
            infile_text: Path to input text file
            save_intermediate: Whether to save intermediate results
            
        Returns:
            Complete analysis results with metrics
        """
        self.performance_data["start_time"] = datetime.now().isoformat()
        self.log(f"="*60, "INFO")
        self.log(f"Starting Enhanced TreeLLM Pipeline", "INFO")
        self.log(f"Preset: {self.preset} | Model: {self.config.model.model_name}", "INFO")
        self.log(f"="*60, "INFO")
        
        # Load input text
        input_path = Path(infile_text)
        raw_text = input_path.read_text(encoding="utf-8")
        input_hash = self._get_input_hash(raw_text)
        
        # Initialize result structure
        result = {
            "metadata": {
                "preset": self.preset,
                "config": self.PRESETS[self.preset],
                "input_file": str(input_path),
                "timestamp": datetime.now().isoformat()
            },
            "stages": {},
            "quality_metrics": None,
            "performance": None
        }
        
        try:
            # Stage 1: Split
            split_result = self._run_split_stage(raw_text, input_hash)
            result["stages"]["split"] = split_result
            if save_intermediate:
                self._save_intermediate("1_split", split_result)
            
            # Stage 2: Build
            build_result = self._run_build_stage(raw_text, input_hash)
            result["stages"]["build"] = build_result
            if save_intermediate:
                self._save_intermediate("2_build", build_result)
            
            # Stage 3: Fuse
            fuse_result = self._run_fuse_stage(build_result, input_hash)
            result["stages"]["fuse"] = fuse_result
            if save_intermediate:
                self._save_intermediate("3_fuse", fuse_result)
            
            # Stage 4: Audit
            audit_result = self._run_audit_stage(split_result, fuse_result, input_hash)
            result["stages"]["audit"] = audit_result
            if save_intermediate:
                self._save_intermediate("4_audit", audit_result)
            
            # Stage 5: Edit Pass 1
            edit1_result = self._run_edit_pass1_stage(
                split_result, fuse_result, audit_result, input_hash
            )
            result["stages"]["edit_pass1"] = edit1_result
            if save_intermediate:
                self._save_intermediate("5_edit_pass1", edit1_result)
            
            # Stage 6: Global Check
            global_result = self._run_global_check_stage(edit1_result, input_hash)
            result["stages"]["global_check"] = global_result
            if save_intermediate:
                self._save_intermediate("6_global_check", global_result)
            
            # Stage 7: Edit Pass 2
            final_result = self._run_edit_pass2_stage(
                edit1_result, global_result, input_hash
            )
            result["stages"]["edit_pass2"] = final_result
            if save_intermediate:
                self._save_intermediate("7_edit_pass2", final_result)
            
            # Add final content
            result["final_output"] = final_result
            
            self.log(f"="*60, "INFO")
            self.log(f"Pipeline completed successfully!", "INFO")
            
        except Exception as e:
            self.log(f"Pipeline failed: {e}", "ERROR")
            result["error"] = str(e)
            raise
        
        finally:
            # Finalize metrics
            self.performance_data["end_time"] = datetime.now().isoformat()
            
            if self.quality_metrics:
                result["quality_metrics"] = {
                    "overall_score": self.quality_metrics.calculate_overall_score(),
                    "detailed": self.quality_metrics.metrics
                }
            
            result["performance"] = self.performance_data
            
            # Calculate total duration
            if self.performance_data["start_time"] and self.performance_data["end_time"]:
                start = datetime.fromisoformat(self.performance_data["start_time"])
                end = datetime.fromisoformat(self.performance_data["end_time"])
                total_duration = (end - start).total_seconds()
                result["performance"]["total_duration"] = total_duration
                
                self.log(f"Total processing time: {total_duration:.2f}s", "INFO")
            
            # Save complete result
            self._save_final_result(result)
            
            if self.quality_metrics:
                self.log(f"Quality Score: {result['quality_metrics']['overall_score']:.2f}/1.0", "INFO")
            
            self.log(f"="*60, "INFO")
        
        return result


def main():
    """Main entry point for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced TreeLLM Pipeline")
    parser.add_argument("input_file", help="Path to input text file")
    parser.add_argument("--preset", choices=["fast", "balanced", "precision", "research"],
                       default="balanced", help="Configuration preset")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-metrics", action="store_true", help="Disable quality metrics")
    
    args = parser.parse_args()
    
    orchestrator = EnhancedOrchestratorV3(
        preset=args.preset,
        enable_metrics=not args.no_metrics,
        enable_caching=not args.no_cache
    )
    
    result = orchestrator.run(args.input_file)
    
    print(f"\nPipeline completed successfully!")
    print(f"Results saved to: {orchestrator.base_dir}")
    
    if not args.no_metrics:
        print(f"Quality Score: {result['quality_metrics']['overall_score']:.2f}/1.0")
    
    print(f"Total Duration: {result['performance'].get('total_duration', 'N/A'):.2f}s")


if __name__ == "__main__":
    main()
