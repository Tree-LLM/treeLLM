#!/usr/bin/env python3
"""
TreeLLM - Enhanced Academic Paper Analysis Pipeline
Main entry point for the TreeLLM system
Version: 3.0
"""

import sys
import argparse
from pathlib import Path
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from Orchestrator import EnhancedOrchestratorV3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for TreeLLM"""
    parser = argparse.ArgumentParser(
        description="TreeLLM - AI-Powered Academic Paper Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sample/example.txt                    # Run with default settings
  %(prog)s paper.txt --preset fast              # Quick analysis
  %(prog)s paper.txt --preset research          # High-quality analysis
  %(prog)s --create-sample                      # Create a sample file
  
Available presets:
  fast      - Quick processing with GPT-3.5-turbo (lowest cost)
  balanced  - Balanced quality and speed (default)
  precision - High precision analysis
  research  - Maximum quality for research

For more information, visit: https://github.com/yourusername/TreeLLM
        """
    )
    
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to input text file"
    )
    
    parser.add_argument(
        "--preset",
        choices=["fast", "balanced", "precision", "research"],
        default="balanced",
        help="Configuration preset (default: balanced)"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (will reprocess even if cached)"
    )
    
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Disable quality metrics tracking"
    )
    
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample file for testing"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system test without API calls"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 3.0"
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY") and not args.test and not args.create_sample:
        logger.error("OPENAI_API_KEY not found in environment variables")
        logger.error("Please set it in .env file or export OPENAI_API_KEY='your-key'")
        return 1
    
    # Handle special commands
    if args.create_sample:
        create_sample_file()
        return 0
    
    if args.test:
        run_system_test()
        return 0
    
    # Check input file
    if not args.input_file:
        # Try to find a sample file
        sample_files = list(Path("sample").glob("*.txt"))
        if sample_files:
            args.input_file = str(sample_files[0])
            logger.info(f"No input specified, using: {args.input_file}")
        else:
            parser.print_help()
            return 1
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1
    
    # Run pipeline
    try:
        logger.info("="*60)
        logger.info("TreeLLM - Academic Paper Analysis Pipeline")
        logger.info(f"Version: 3.0 | Preset: {args.preset}")
        logger.info("="*60)
        
        orchestrator = EnhancedOrchestratorV3(
            preset=args.preset,
            enable_metrics=not args.no_metrics,
            enable_caching=not args.no_cache
        )
        
        result = orchestrator.run(str(input_path))
        
        # Display summary
        if result.get("quality_metrics"):
            score = result["quality_metrics"]["overall_score"]
            logger.info(f"Quality Score: {score:.2f}/1.0")
        
        if result.get("performance"):
            duration = result["performance"].get("total_duration", 0)
            logger.info(f"Processing Time: {duration:.1f} seconds")
        
        logger.info("="*60)
        logger.info("Analysis completed successfully!")
        logger.info(f"Results saved to: {orchestrator.base_dir}")
        logger.info("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1

def create_sample_file():
    """Create a sample file for testing"""
    sample_dir = Path("sample")
    sample_dir.mkdir(exist_ok=True)
    
    sample_file = sample_dir / "sample_paper.txt"
    
    content = """# Sample Academic Paper for TreeLLM

## Abstract
This paper presents TreeLLM, a comprehensive pipeline for analyzing academic papers using large language models. The system processes papers through seven stages, each optimized for specific aspects of document analysis.

## Introduction
Academic paper analysis is a crucial task in research. Traditional methods often struggle with maintaining consistency and capturing hierarchical relationships. TreeLLM addresses these challenges through a structured pipeline approach.

## Methodology
The TreeLLM pipeline consists of:
1. Document Splitting - Intelligent segmentation
2. Information Extraction - Using optimized prompts
3. Tree Construction - Hierarchical organization
4. Quality Audit - Based on academic standards
5. First Refinement - Initial improvements
6. Global Check - Cross-section consistency
7. Final Refinement - Output optimization

## Results
TreeLLM achieves high accuracy in paper analysis with an F1-score of 0.93 on our test dataset.

## Conclusion
TreeLLM provides an effective solution for automated academic paper analysis, maintaining both accuracy and consistency throughout the process.
"""
    
    sample_file.write_text(content)
    logger.info(f"Created sample file: {sample_file}")
    logger.info(f"You can now run: python main.py {sample_file}")

def run_system_test():
    """Run system test without API calls"""
    logger.info("Running system test (no API calls)...")
    
    try:
        # Test imports
        from module.split import run as split_run
        from module.build import BuildStep
        from module.fuse import TreeBuilder
        logger.info("✓ All modules imported successfully")
        
        # Test configuration
        from config import TreeLLMConfig
        config = TreeLLMConfig()
        config.validate()
        logger.info("✓ Configuration valid")
        
        # Test orchestrator initialization
        orchestrator = EnhancedOrchestratorV3(preset="balanced")
        logger.info("✓ Orchestrator initialized")
        
        # Test split module
        test_text = "# Title\n## Section\nContent"
        result = split_run(test_text)
        logger.info(f"✓ Split module works: {len(result)} sections")
        
        logger.info("\n✅ All tests passed! System is ready.")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    sys.exit(main())
