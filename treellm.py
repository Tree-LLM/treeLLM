#!/usr/bin/env python3
"""
TreeLLM V3 - Unified Main Entry Point
통합 실행 스크립트
"""

import sys
import argparse
from pathlib import Path
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup paths
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """환경 체크"""
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️  OPENAI_API_KEY not found in .env file")
        logger.warning("   Please set: OPENAI_API_KEY=sk-your-key")
        return False
    return True

def run_web():
    """웹 인터페이스 실행"""
    logger.info("🌐 Starting Web Interface...")
    logger.info("   Open browser at: http://localhost:5001")
    from app import app
    app.run(host='0.0.0.0', port=5001, debug=False)

def run_cli(args):
    """CLI 모드 실행"""
    from Orchestrator import EnhancedOrchestratorV3
    
    logger.info(f"📄 Processing: {args.input}")
    logger.info(f"⚙️  Preset: {args.preset}")
    
    orchestrator = EnhancedOrchestratorV3(
        preset=args.preset,
        enable_metrics=not args.no_metrics,
        enable_caching=not args.no_cache
    )
    
    result = orchestrator.run(args.input)
    
    if "quality_metrics" in result:
        score = result["quality_metrics"]["overall_score"]
        logger.info(f"✅ Quality Score: {score:.2f}")
    
    if "performance" in result:
        duration = result["performance"].get("total_duration", 0)
        logger.info(f"⏱️  Processing Time: {duration:.1f}s")
    
    logger.info(f"💾 Results saved to: results/")
    return result

def run_test():
    """테스트 실행"""
    logger.info("🧪 Running System Tests...")
    import test_system
    test_system.main()

def create_sample():
    """샘플 파일 생성"""
    sample_file = Path("sample/test_paper.txt")
    content = """# Sample Paper for TreeLLM

## Abstract
This is a test paper for TreeLLM system testing.

## Introduction
The introduction provides background information about the research.

## Methodology
We use a seven-stage pipeline to process papers.

## Results
The system successfully processes academic papers.

## Conclusion
TreeLLM provides an effective pipeline for analysis."""
    
    sample_file.write_text(content)
    logger.info(f"✅ Sample file created: {sample_file}")
    return sample_file

def main():
    parser = argparse.ArgumentParser(
        description="TreeLLM V3 - AI-Powered Academic Paper Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --web                    # Start web interface
  %(prog)s paper.txt                # Process paper with default preset
  %(prog)s paper.txt --preset fast  # Use fast preset
  %(prog)s --test                   # Run system tests
  %(prog)s --create-sample          # Create sample file
        """
    )
    
    parser.add_argument("input", nargs="?", help="Input file path")
    parser.add_argument("--web", action="store_true", help="Start web interface")
    parser.add_argument("--preset", choices=["fast", "balanced", "precision", "research"],
                       default="balanced", help="Processing preset")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-metrics", action="store_true", help="Disable metrics")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--create-sample", action="store_true", help="Create sample file")
    
    args = parser.parse_args()
    
    # Logo
    print("""
╔══════════════════════════════════════╗
║       🌳 TreeLLM V3.0 Enhanced       ║
║   Academic Paper Analysis Pipeline   ║
╚══════════════════════════════════════╝
    """)
    
    # Environment check
    if not args.test and not args.create_sample:
        if not check_environment():
            if not args.web:  # Web mode can show the error in UI
                return 1
    
    # Execute based on mode
    try:
        if args.web:
            run_web()
        elif args.test:
            run_test()
        elif args.create_sample:
            sample = create_sample()
            print(f"\n💡 You can now run: python {Path(__file__).name} {sample}")
        elif args.input:
            run_cli(args)
        else:
            # No arguments - show help
            parser.print_help()
            print("\n💡 Quick Start:")
            print("   python treellm.py --web           # Web interface")
            print("   python treellm.py --test          # Run tests")
            print("   python treellm.py sample.txt      # Process file")
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
