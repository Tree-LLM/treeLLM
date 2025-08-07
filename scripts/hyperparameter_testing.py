"""
Hyperparameter Testing Suite for TreeLLM
─────────────────────────────────────────
Automated testing and optimization for academic paper analysis pipeline
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import hashlib
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from Orchestrator import EnhancedOrchestratorV3, QualityMetrics
from config import TreeLLMConfig, ModelConfig


class HyperparameterTester:
    """Comprehensive hyperparameter testing framework"""
    
    def __init__(self, test_papers_dir: str = "sample", output_dir: str = "hyperparameter_tests"):
        """
        Initialize the hyperparameter tester
        
        Args:
            test_papers_dir: Directory containing test papers
            output_dir: Directory for test results
        """
        self.test_papers_dir = Path(test_papers_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Test results storage
        self.results = []
        self.best_configs = {}
        
        # Cost tracking (approximate)
        self.cost_per_1k_tokens = {
            "gpt-4o": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002
        }
    
    def _setup_logging(self):
        """Setup logging for testing"""
        log_file = self.output_dir / f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_test_configurations(self) -> Dict[str, Dict]:
        """Generate test configurations for hyperparameter grid search"""
        
        configurations = {}
        
        # 1. Temperature variations (keeping other params constant)
        for temp in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
            config_name = f"temp_{temp}"
            configurations[config_name] = {
                "model": "gpt-4o",
                "temperature": temp,
                "top_p": 0.3,
                "max_tokens": 4096,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "test_type": "temperature"
            }
        
        # 2. Top-p variations
        for top_p in [0.1, 0.3, 0.5, 0.7, 0.9]:
            config_name = f"top_p_{top_p}"
            configurations[config_name] = {
                "model": "gpt-4o",
                "temperature": 0.2,  # Use optimal from previous test
                "top_p": top_p,
                "max_tokens": 4096,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "test_type": "top_p"
            }
        
        # 3. Max tokens variations
        for max_tokens in [2048, 3072, 4096, 6144, 8192]:
            config_name = f"max_tokens_{max_tokens}"
            configurations[config_name] = {
                "model": "gpt-4o",
                "temperature": 0.2,
                "top_p": 0.3,
                "max_tokens": max_tokens,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "test_type": "max_tokens"
            }
        
        # 4. Penalty variations
        for freq_penalty in [0.0, 0.1, 0.2, 0.3]:
            for pres_penalty in [0.0, 0.05, 0.1]:
                config_name = f"penalties_f{freq_penalty}_p{pres_penalty}"
                configurations[config_name] = {
                    "model": "gpt-4o",
                    "temperature": 0.2,
                    "top_p": 0.3,
                    "max_tokens": 4096,
                    "frequency_penalty": freq_penalty,
                    "presence_penalty": pres_penalty,
                    "test_type": "penalties"
                }
        
        # 5. Stage-specific optimized configurations
        configurations["stage_optimized"] = {
            "model": "gpt-4o",
            "stage_specific": True,
            "stages": {
                "split": {"temperature": 0.1, "top_p": 0.1, "max_tokens": 2048},
                "build": {"temperature": 0.2, "top_p": 0.3, "max_tokens": 4096},
                "fuse": {"temperature": 0.15, "top_p": 0.2, "max_tokens": 6144},
                "audit": {"temperature": 0.05, "top_p": 0.1, "max_tokens": 3072},
                "edit_pass1": {"temperature": 0.25, "top_p": 0.4, "max_tokens": 4096},
                "global_check": {"temperature": 0.1, "top_p": 0.2, "max_tokens": 3072},
                "edit_pass2": {"temperature": 0.2, "top_p": 0.3, "max_tokens": 4096}
            },
            "test_type": "stage_specific"
        }
        
        # 6. Model comparison
        for model in ["gpt-3.5-turbo", "gpt-4o"]:
            config_name = f"model_{model.replace('.', '_')}"
            configurations[config_name] = {
                "model": model,
                "temperature": 0.3 if model == "gpt-3.5-turbo" else 0.2,
                "top_p": 0.4 if model == "gpt-3.5-turbo" else 0.3,
                "max_tokens": 4096,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "test_type": "model_comparison"
            }
        
        return configurations
    
    def run_single_test(self, paper_path: Path, config_name: str, 
                       config: Dict) -> Dict[str, Any]:
        """
        Run a single test with given configuration
        
        Args:
            paper_path: Path to test paper
            config_name: Name of configuration
            config: Configuration dictionary
            
        Returns:
            Test results dictionary
        """
        self.logger.info(f"Testing {config_name} on {paper_path.name}")
        
        start_time = time.time()
        
        try:
            # Create custom config
            if config.get("stage_specific"):
                # Use stage-specific configuration
                orchestrator = EnhancedOrchestratorV3(
                    preset="balanced",
                    enable_metrics=True,
                    enable_caching=False  # Disable for fair comparison
                )
                # Override with stage-specific params
                orchestrator.stage_params = config["stages"]
            else:
                # Create config with specified parameters
                tree_config = TreeLLMConfig()
                tree_config.model.model_name = config["model"]
                tree_config.model.temperature = config["temperature"]
                tree_config.model.top_p = config["top_p"]
                tree_config.model.max_tokens = config["max_tokens"]
                tree_config.model.frequency_penalty = config["frequency_penalty"]
                tree_config.model.presence_penalty = config["presence_penalty"]
                
                orchestrator = EnhancedOrchestratorV3(
                    config=tree_config,
                    enable_metrics=True,
                    enable_caching=False
                )
            
            # Run pipeline
            result = orchestrator.run(str(paper_path), save_intermediate=False)
            
            # Calculate metrics
            duration = time.time() - start_time
            
            # Extract quality metrics
            quality_score = 0.0
            if "quality_metrics" in result:
                quality_score = result["quality_metrics"]["overall_score"]
            
            # Estimate cost
            total_tokens = result.get("performance", {}).get("total_tokens", 0)
            model_name = config.get("model", "gpt-4o")
            estimated_cost = (total_tokens / 1000) * self.cost_per_1k_tokens.get(model_name, 0.01)
            
            test_result = {
                "config_name": config_name,
                "paper": paper_path.name,
                "success": True,
                "duration": duration,
                "quality_score": quality_score,
                "total_tokens": total_tokens,
                "estimated_cost": estimated_cost,
                "config": config,
                "stage_metrics": result.get("performance", {}).get("stage_metrics", {}),
                "detailed_metrics": result.get("quality_metrics", {}).get("detailed", {})
            }
            
            self.logger.info(f"✓ {config_name} - Score: {quality_score:.3f}, Time: {duration:.1f}s, Cost: ${estimated_cost:.3f}")
            
        except Exception as e:
            self.logger.error(f"✗ {config_name} failed: {e}")
            test_result = {
                "config_name": config_name,
                "paper": paper_path.name,
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
                "quality_score": 0.0,
                "config": config
            }
        
        return test_result
    
    def run_grid_search(self, num_papers: int = 3, parallel: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive grid search on hyperparameters
        
        Args:
            num_papers: Number of test papers to use
            parallel: Whether to run tests in parallel
            
        Returns:
            Analysis results
        """
        self.logger.info("="*60)
        self.logger.info("Starting Hyperparameter Grid Search")
        self.logger.info("="*60)
        
        # Get test papers
        test_papers = list(self.test_papers_dir.glob("*.txt"))[:num_papers]
        if not test_papers:
            raise ValueError(f"No test papers found in {self.test_papers_dir}")
        
        self.logger.info(f"Using {len(test_papers)} test papers")
        
        # Generate configurations
        configurations = self.generate_test_configurations()
        self.logger.info(f"Testing {len(configurations)} configurations")
        
        # Run tests
        all_results = []
        
        if parallel:
            # Parallel execution
            with ProcessPoolExecutor(max_workers=2) as executor:
                futures = []
                for paper_path in test_papers:
                    for config_name, config in configurations.items():
                        future = executor.submit(
                            self.run_single_test, paper_path, config_name, config
                        )
                        futures.append(future)
                
                for future in as_completed(futures):
                    result = future.result()
                    all_results.append(result)
                    self.results.append(result)
        else:
            # Sequential execution
            for paper_path in test_papers:
                for config_name, config in configurations.items():
                    result = self.run_single_test(paper_path, config_name, config)
                    all_results.append(result)
                    self.results.append(result)
        
        # Analyze results
        analysis = self.analyze_results(all_results)
        
        # Save results
        self.save_results(analysis)
        
        return analysis
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze test results to find optimal configurations
        
        Args:
            results: List of test results
            
        Returns:
            Analysis dictionary
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("Analyzing Results")
        self.logger.info("="*60)
        
        analysis = {
            "summary": {},
            "best_configs": {},
            "parameter_impacts": {},
            "recommendations": []
        }
        
        # Group results by test type
        test_types = {}
        for result in results:
            if not result["success"]:
                continue
            
            test_type = result["config"].get("test_type", "unknown")
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        # Analyze each test type
        for test_type, type_results in test_types.items():
            if not type_results:
                continue
            
            # Calculate average scores
            scores_by_config = {}
            for result in type_results:
                config_name = result["config_name"]
                if config_name not in scores_by_config:
                    scores_by_config[config_name] = {
                        "scores": [],
                        "durations": [],
                        "costs": []
                    }
                scores_by_config[config_name]["scores"].append(result["quality_score"])
                scores_by_config[config_name]["durations"].append(result["duration"])
                scores_by_config[config_name]["costs"].append(result.get("estimated_cost", 0))
            
            # Find best configuration for this test type
            best_config = None
            best_score = 0
            
            for config_name, metrics in scores_by_config.items():
                avg_score = np.mean(metrics["scores"])
                avg_duration = np.mean(metrics["durations"])
                avg_cost = np.mean(metrics["costs"])
                
                # Composite score (weighted)
                composite = avg_score * 0.7 - (avg_duration / 1000) * 0.2 - avg_cost * 0.1
                
                if composite > best_score:
                    best_score = composite
                    best_config = {
                        "name": config_name,
                        "avg_quality": avg_score,
                        "avg_duration": avg_duration,
                        "avg_cost": avg_cost,
                        "composite_score": composite
                    }
            
            analysis["best_configs"][test_type] = best_config
            
            # Log best config for this test type
            if best_config:
                self.logger.info(f"\nBest {test_type}: {best_config['name']}")
                self.logger.info(f"  Quality: {best_config['avg_quality']:.3f}")
                self.logger.info(f"  Duration: {best_config['avg_duration']:.1f}s")
                self.logger.info(f"  Cost: ${best_config['avg_cost']:.3f}")
        
        # Generate parameter impact analysis
        if "temperature" in test_types:
            temp_impact = self._analyze_parameter_impact(
                test_types["temperature"], "temperature"
            )
            analysis["parameter_impacts"]["temperature"] = temp_impact
        
        if "top_p" in test_types:
            top_p_impact = self._analyze_parameter_impact(
                test_types["top_p"], "top_p"
            )
            analysis["parameter_impacts"]["top_p"] = top_p_impact
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # Overall summary
        all_successful = [r for r in results if r["success"]]
        if all_successful:
            analysis["summary"] = {
                "total_tests": len(results),
                "successful_tests": len(all_successful),
                "avg_quality_score": np.mean([r["quality_score"] for r in all_successful]),
                "avg_duration": np.mean([r["duration"] for r in all_successful]),
                "total_cost": sum([r.get("estimated_cost", 0) for r in all_successful])
            }
        
        return analysis
    
    def _analyze_parameter_impact(self, results: List[Dict], 
                                 param_name: str) -> Dict[str, Any]:
        """
        Analyze the impact of a specific parameter on performance
        
        Args:
            results: Test results for this parameter
            param_name: Name of parameter being analyzed
            
        Returns:
            Impact analysis
        """
        impact = {
            "parameter": param_name,
            "values_tested": [],
            "quality_trend": [],
            "duration_trend": [],
            "optimal_value": None
        }
        
        # Group by parameter value
        by_value = {}
        for result in results:
            value = result["config"][param_name]
            if value not in by_value:
                by_value[value] = []
            by_value[value].append(result)
        
        # Calculate trends
        best_quality = 0
        for value in sorted(by_value.keys()):
            value_results = by_value[value]
            avg_quality = np.mean([r["quality_score"] for r in value_results])
            avg_duration = np.mean([r["duration"] for r in value_results])
            
            impact["values_tested"].append(value)
            impact["quality_trend"].append(avg_quality)
            impact["duration_trend"].append(avg_duration)
            
            if avg_quality > best_quality:
                best_quality = avg_quality
                impact["optimal_value"] = value
        
        return impact
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Generate recommendations based on analysis
        
        Args:
            analysis: Analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Temperature recommendation
        if "temperature" in analysis["parameter_impacts"]:
            optimal_temp = analysis["parameter_impacts"]["temperature"]["optimal_value"]
            recommendations.append(
                f"Optimal temperature: {optimal_temp} - Lower values improve consistency for academic papers"
            )
        
        # Top-p recommendation
        if "top_p" in analysis["parameter_impacts"]:
            optimal_top_p = analysis["parameter_impacts"]["top_p"]["optimal_value"]
            recommendations.append(
                f"Optimal top_p: {optimal_top_p} - Narrow sampling improves precision"
            )
        
        # Stage-specific recommendation
        if "stage_specific" in analysis["best_configs"]:
            recommendations.append(
                "Use stage-specific parameters for optimal results - Different stages benefit from different settings"
            )
        
        # Model recommendation
        if "model_comparison" in analysis["best_configs"]:
            best_model = analysis["best_configs"]["model_comparison"]
            if best_model["name"].startswith("model_gpt-4"):
                recommendations.append(
                    "GPT-4 variants provide better quality for academic analysis despite higher cost"
                )
            else:
                recommendations.append(
                    "Consider GPT-3.5-turbo for draft analysis to reduce costs"
                )
        
        return recommendations
    
    def save_results(self, analysis: Dict):
        """Save test results and analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = self.output_dir / f"test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save analysis
        analysis_file = self.output_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save summary report
        report_file = self.output_dir / f"report_{timestamp}.md"
        self._generate_report(analysis, report_file)
        
        self.logger.info(f"\nResults saved to {self.output_dir}")
        self.logger.info(f"  - Results: {results_file.name}")
        self.logger.info(f"  - Analysis: {analysis_file.name}")
        self.logger.info(f"  - Report: {report_file.name}")
    
    def _generate_report(self, analysis: Dict, output_path: Path):
        """Generate markdown report from analysis"""
        report = []
        report.append("# TreeLLM Hyperparameter Test Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        if "summary" in analysis:
            s = analysis["summary"]
            report.append("## Summary")
            report.append(f"- Total Tests: {s.get('total_tests', 0)}")
            report.append(f"- Successful: {s.get('successful_tests', 0)}")
            report.append(f"- Average Quality Score: {s.get('avg_quality_score', 0):.3f}")
            report.append(f"- Average Duration: {s.get('avg_duration', 0):.1f}s")
            report.append(f"- Total Cost: ${s.get('total_cost', 0):.2f}\n")
        
        # Best Configurations
        report.append("## Best Configurations by Test Type\n")
        for test_type, config in analysis.get("best_configs", {}).items():
            if config:
                report.append(f"### {test_type}")
                report.append(f"- **Winner**: {config['name']}")
                report.append(f"- Quality Score: {config['avg_quality']:.3f}")
                report.append(f"- Processing Time: {config['avg_duration']:.1f}s")
                report.append(f"- Estimated Cost: ${config['avg_cost']:.3f}")
                report.append(f"- Composite Score: {config['composite_score']:.3f}\n")
        
        # Parameter Impacts
        if "parameter_impacts" in analysis:
            report.append("## Parameter Impact Analysis\n")
            for param, impact in analysis["parameter_impacts"].items():
                report.append(f"### {param}")
                report.append(f"- Optimal Value: **{impact['optimal_value']}**")
                report.append(f"- Values Tested: {impact['values_tested']}")
                report.append(f"- Quality Trend: {[f'{q:.3f}' for q in impact['quality_trend']]}\n")
        
        # Recommendations
        if "recommendations" in analysis:
            report.append("## Recommendations\n")
            for i, rec in enumerate(analysis["recommendations"], 1):
                report.append(f"{i}. {rec}")
        
        # Write report
        output_path.write_text("\n".join(report))
    
    def run_incremental_optimization(self, paper_path: Path) -> Dict[str, Any]:
        """
        Run incremental optimization to find best parameters
        
        Args:
            paper_path: Path to test paper
            
        Returns:
            Optimal configuration
        """
        self.logger.info("Starting Incremental Optimization")
        
        # Start with baseline
        best_config = {
            "model": "gpt-4o",
            "temperature": 0.3,
            "top_p": 0.3,
            "max_tokens": 4096,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        best_score = 0
        
        # Optimize temperature
        self.logger.info("\nOptimizing temperature...")
        for temp in [0.0, 0.1, 0.2, 0.3, 0.4]:
            config = best_config.copy()
            config["temperature"] = temp
            result = self.run_single_test(paper_path, f"temp_{temp}", config)
            
            if result["success"] and result["quality_score"] > best_score:
                best_score = result["quality_score"]
                best_config["temperature"] = temp
        
        self.logger.info(f"Best temperature: {best_config['temperature']}")
        
        # Optimize top_p
        self.logger.info("\nOptimizing top_p...")
        for top_p in [0.1, 0.2, 0.3, 0.4, 0.5]:
            config = best_config.copy()
            config["top_p"] = top_p
            result = self.run_single_test(paper_path, f"top_p_{top_p}", config)
            
            if result["success"] and result["quality_score"] > best_score:
                best_score = result["quality_score"]
                best_config["top_p"] = top_p
        
        self.logger.info(f"Best top_p: {best_config['top_p']}")
        
        # Optimize penalties
        self.logger.info("\nOptimizing penalties...")
        for freq_pen in [0.0, 0.1, 0.2]:
            for pres_pen in [0.0, 0.05, 0.1]:
                config = best_config.copy()
                config["frequency_penalty"] = freq_pen
                config["presence_penalty"] = pres_pen
                result = self.run_single_test(
                    paper_path, 
                    f"pen_f{freq_pen}_p{pres_pen}", 
                    config
                )
                
                if result["success"] and result["quality_score"] > best_score:
                    best_score = result["quality_score"]
                    best_config["frequency_penalty"] = freq_pen
                    best_config["presence_penalty"] = pres_pen
        
        self.logger.info(f"Best frequency_penalty: {best_config['frequency_penalty']}")
        self.logger.info(f"Best presence_penalty: {best_config['presence_penalty']}")
        
        return {
            "optimal_config": best_config,
            "best_score": best_score
        }


def main():
    """Main entry point for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TreeLLM Hyperparameter Testing")
    parser.add_argument("--test-type", choices=["grid", "incremental", "quick"],
                       default="quick", help="Type of test to run")
    parser.add_argument("--num-papers", type=int, default=2,
                       help="Number of test papers")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--test-dir", default="sample",
                       help="Directory containing test papers")
    parser.add_argument("--output-dir", default="hyperparameter_tests",
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    tester = HyperparameterTester(
        test_papers_dir=args.test_dir,
        output_dir=args.output_dir
    )
    
    if args.test_type == "grid":
        # Full grid search
        results = tester.run_grid_search(
            num_papers=args.num_papers,
            parallel=args.parallel
        )
        print("\n" + "="*60)
        print("GRID SEARCH COMPLETE")
        print("="*60)
        for rec in results.get("recommendations", []):
            print(f"• {rec}")
    
    elif args.test_type == "incremental":
        # Incremental optimization
        test_papers = list(Path(args.test_dir).glob("*.txt"))[:1]
        if test_papers:
            result = tester.run_incremental_optimization(test_papers[0])
            print("\n" + "="*60)
            print("OPTIMAL CONFIGURATION FOUND")
            print("="*60)
            for key, value in result["optimal_config"].items():
                print(f"{key}: {value}")
            print(f"\nBest Score: {result['best_score']:.3f}")
    
    else:  # quick test
        # Quick test with presets
        print("Running quick test with presets...")
        test_papers = list(Path(args.test_dir).glob("*.txt"))[:1]
        if test_papers:
            for preset in ["fast", "balanced", "precision"]:
                print(f"\nTesting preset: {preset}")
                orchestrator = EnhancedOrchestratorV3(preset=preset)
                result = orchestrator.run(str(test_papers[0]))
                
                if "quality_metrics" in result:
                    score = result["quality_metrics"]["overall_score"]
                    duration = result["performance"].get("total_duration", 0)
                    print(f"  Score: {score:.3f}, Duration: {duration:.1f}s")


if __name__ == "__main__":
    main()
