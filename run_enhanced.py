#!/usr/bin/env python3
"""
Simple runner script for TreeLLM V3 Enhanced
This script provides a simple way to run the pipeline with proper error handling
"""

import sys
import os
from pathlib import Path
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly set up"""
    issues = []
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("OPENAI_API_KEY not found. Please set it in .env file or environment")
    
    # Check sample directory
    sample_dir = Path("sample")
    if not sample_dir.exists():
        sample_dir.mkdir(exist_ok=True)
        logger.info(f"Created sample directory: {sample_dir}")
    
    # Check results directory
    results_dir = Path("results")
    if not results_dir.exists():
        results_dir.mkdir(exist_ok=True)
        logger.info(f"Created results directory: {results_dir}")
    
    # Check for sample files
    sample_files = list(sample_dir.glob("*.txt"))
    if not sample_files:
        # Create a default sample file
        create_sample_file()
    
    return issues

def create_sample_file():
    """Create a default sample file for testing"""
    sample_file = Path("sample/test_paper.txt")
    content = """# Sample Academic Paper for TreeLLM Testing

## Abstract
This paper presents a comprehensive analysis of large language models (LLMs) in academic research. We investigate the effectiveness of hierarchical processing pipelines for extracting and structuring information from scholarly publications. Our approach demonstrates significant improvements in accuracy and consistency compared to traditional methods.

## Introduction
The rapid advancement of large language models has opened new possibilities for automated analysis of academic literature. Traditional approaches to paper analysis often struggle with maintaining consistency across different sections and capturing the hierarchical nature of scholarly arguments.

In this work, we present TreeLLM, a novel pipeline that processes academic papers through seven distinct stages, each optimized for specific aspects of document analysis. Our system addresses three key challenges:

1. Maintaining semantic consistency across document sections
2. Preserving hierarchical relationships in complex arguments
3. Ensuring reproducibility and quality control

## Related Work
Previous approaches to automated paper analysis have primarily focused on either keyword extraction or summarization. Smith et al. (2023) proposed a neural approach for citation network analysis, while Johnson and Lee (2022) developed methods for abstract generation.

Our work builds upon these foundations but introduces a more comprehensive pipeline that considers the full document structure and maintains context throughout the processing stages.

## Methodology
TreeLLM employs a seven-stage pipeline:

### Stage 1: Document Splitting
The input document is intelligently segmented into logical sections, preserving the natural structure of academic papers.

### Stage 2: Information Extraction
Each section is processed using optimized prompts to extract key information, claims, and evidence.

### Stage 3: Tree Construction
Extracted information is organized into a hierarchical tree structure that reflects the logical flow of arguments.

### Stage 4: Quality Audit
The constructed tree undergoes rigorous quality checks based on academic standards.

### Stage 5: First Refinement Pass
Initial improvements are made based on audit feedback, focusing on clarity and completeness.

### Stage 6: Global Consistency Check
Cross-section consistency is verified to ensure coherent representation of the entire document.

### Stage 7: Final Refinement
Final adjustments are made to optimize the output for downstream applications.

## Experiments
We evaluated TreeLLM on a dataset of 500 academic papers from various disciplines. Our experiments measured:

- Extraction accuracy: 94.3% precision, 91.7% recall
- Structural preservation: 89.2% hierarchical consistency
- Processing efficiency: Average 5.3 minutes per paper

### Baseline Comparisons
Compared to existing methods:
- Traditional keyword extraction: 67% F1 score
- Neural summarization: 78% F1 score
- TreeLLM (ours): 93% F1 score

## Results
TreeLLM demonstrates superior performance across all evaluated metrics. The stage-specific optimization particularly benefits:

1. Complex multi-disciplinary papers
2. Papers with extensive mathematical formulations
3. Documents with nested argumentative structures

### Ablation Study
Removing individual stages from the pipeline resulted in:
- Without Stage 4 (Audit): -12% quality score
- Without Stage 6 (Global Check): -8% consistency
- Without Stage 7 (Final Refinement): -5% readability

## Discussion
The success of TreeLLM can be attributed to three design principles:

1. **Stage-specific optimization**: Each stage uses tailored hyperparameters
2. **Hierarchical preservation**: Maintaining document structure throughout processing
3. **Quality-driven iteration**: Multiple refinement passes ensure high-quality output

### Limitations
Current limitations include:
- Processing time for very long documents (>50 pages)
- Handling of non-English content
- Domain-specific terminology in highly specialized fields

## Conclusion
TreeLLM represents a significant advancement in automated academic paper analysis. By combining stage-specific optimization with hierarchical processing, our system achieves state-of-the-art performance while maintaining interpretability and consistency.

Future work will focus on:
- Multilingual support
- Real-time processing capabilities
- Integration with citation databases

## References
1. Smith, J., et al. (2023). "Neural Citation Networks." Journal of AI Research.
2. Johnson, M., & Lee, S. (2022). "Automated Abstract Generation." NLP Proceedings.
3. Brown, T., et al. (2020). "Language Models are Few-Shot Learners." NeurIPS.
"""
    
    sample_file.write_text(content)
    logger.info(f"Created sample file: {sample_file}")
    return sample_file

def run_pipeline(input_file, preset="balanced", use_cache=True):
    """Run the TreeLLM pipeline"""
    try:
        # Import here to avoid import errors if environment not set up
        from Orchestrator import EnhancedOrchestratorV3
        
        logger.info(f"Starting pipeline with preset: {preset}")
        logger.info(f"Input file: {input_file}")
        
        # Create orchestrator
        orchestrator = EnhancedOrchestratorV3(
            preset=preset,
            enable_metrics=True,
            enable_caching=use_cache
        )
        
        # Run pipeline
        result = orchestrator.run(str(input_file))
        
        # Report results
        if "quality_metrics" in result:
            score = result["quality_metrics"]["overall_score"]
            logger.info(f"Analysis completed with quality score: {score:.2f}")
        
        if "performance" in result:
            duration = result["performance"].get("total_duration", 0)
            logger.info(f"Total processing time: {duration:.1f} seconds")
        
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TreeLLM V3 Enhanced - Academic Paper Analysis Pipeline"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file path (optional, will use sample if not provided)"
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
        help="Disable caching"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample file and exit"
    )
    
    args = parser.parse_args()
    
    # Check environment
    issues = check_environment()
    if issues:
        logger.error("Environment issues found:")
        for issue in issues:
            logger.error(f"  - {issue}")
        logger.error("Please fix these issues before running the pipeline")
        return 1
    
    # Handle sample creation
    if args.create_sample:
        sample_file = create_sample_file()
        logger.info(f"Sample file created: {sample_file}")
        logger.info(f"You can now run: python {sys.argv[0]} {sample_file}")
        return 0
    
    # Determine input file
    if args.input:
        input_file = Path(args.input)
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            return 1
    else:
        # Use first available sample file
        sample_files = list(Path("sample").glob("*.txt"))
        if sample_files:
            input_file = sample_files[0]
            logger.info(f"No input specified, using: {input_file}")
        else:
            logger.error("No input file specified and no sample files found")
            logger.info("Run with --create-sample to create a sample file")
            return 1
    
    # Run pipeline
    try:
        result = run_pipeline(
            input_file,
            preset=args.preset,
            use_cache=not args.no_cache
        )
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Results saved to: results/")
        
        return 0
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
