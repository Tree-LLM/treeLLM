#!/usr/bin/env python3
"""
Quick test script for TreeLLM V3 Enhanced
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from Orchestrator import EnhancedOrchestratorV3
        print("✓ EnhancedOrchestratorV3 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import EnhancedOrchestratorV3: {e}")
        return False
    
    try:
        from config import TreeLLMConfig, ModelConfig
        print("✓ Config modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from module.build import BuildStep
        from module.split import run as split_run
        from module.fuse import TreeBuilder
        from module.audit import AuditStep
        from module.edit_pass1 import EditPass1
        from module.global_check import GlobalCheck
        from module.edit_pass2 import EditPass2
        print("✓ All pipeline modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pipeline modules: {e}")
        return False
    
    return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from config import TreeLLMConfig
        
        config = TreeLLMConfig()
        config.validate()
        print("✓ Default configuration is valid")
        
        # Test presets
        from Orchestrator import EnhancedOrchestratorV3
        for preset in ["fast", "balanced", "precision", "research"]:
            orchestrator = EnhancedOrchestratorV3(preset=preset)
            print(f"✓ Preset '{preset}' loaded successfully")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_sample_file():
    """Check if sample file exists"""
    print("\nChecking sample files...")
    sample_dir = Path("sample")
    
    if not sample_dir.exists():
        print(f"✗ Sample directory not found: {sample_dir}")
        return False
    
    sample_files = list(sample_dir.glob("*.txt"))
    if sample_files:
        print(f"✓ Found {len(sample_files)} sample file(s):")
        for f in sample_files[:3]:  # Show first 3
            print(f"  - {f.name}")
        return True
    else:
        print("✗ No sample files found")
        # Create a simple sample file
        sample_file = sample_dir / "test_paper.txt"
        sample_file.write_text("""
# Test Paper for TreeLLM

## Abstract
This is a test paper for the TreeLLM system. It contains minimal content for testing purposes.

## Introduction
The introduction section provides background information about the research topic.
This system is designed to analyze academic papers using large language models.

## Methodology
We use a seven-stage pipeline to process academic papers:
1. Split - Divide the paper into sections
2. Build - Extract information using GPT
3. Fuse - Create tree structure
4. Audit - Quality check
5. Edit Pass 1 - Initial improvements
6. Global Check - Consistency verification
7. Edit Pass 2 - Final refinements

## Results
The system successfully processes academic papers and provides structured analysis.

## Conclusion
TreeLLM provides an effective pipeline for academic paper analysis.
        """)
        print(f"✓ Created sample file: {sample_file}")
        return True

def test_api_key():
    """Check if OpenAI API key is set"""
    print("\nChecking API key...")
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if os.getenv("OPENAI_API_KEY"):
        key = os.getenv("OPENAI_API_KEY")
        if key.startswith("sk-"):
            print("✓ OpenAI API key is set")
            return True
        else:
            print("⚠ OpenAI API key found but format looks incorrect")
            return False
    else:
        print("✗ OPENAI_API_KEY not found in environment")
        print("  Please set it in .env file or export OPENAI_API_KEY='your-key'")
        return False

def run_mini_test():
    """Run a minimal test of the pipeline"""
    print("\nRunning mini pipeline test...")
    
    try:
        from Orchestrator import EnhancedOrchestratorV3
        from pathlib import Path
        
        # Find a sample file
        sample_files = list(Path("sample").glob("*.txt"))
        if not sample_files:
            print("✗ No sample files available for testing")
            return False
        
        test_file = sample_files[0]
        print(f"  Using test file: {test_file}")
        
        # Create orchestrator with fast preset for testing
        orchestrator = EnhancedOrchestratorV3(
            preset="fast",
            enable_metrics=True,
            enable_caching=True
        )
        
        # Test just the split stage
        print("  Testing split stage...")
        raw_text = test_file.read_text(encoding="utf-8")
        input_hash = orchestrator._get_input_hash(raw_text)
        
        try:
            result = orchestrator._run_split_stage(raw_text, input_hash)
            if result:
                print(f"  ✓ Split stage completed: {len(result)} sections found")
                return True
            else:
                print("  ✗ Split stage returned empty result")
                return False
        except Exception as e:
            print(f"  ✗ Split stage failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Mini test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("TreeLLM V3 Enhanced - System Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Sample Files", test_sample_file),
        ("API Key Check", test_api_key),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n### {test_name} ###")
        result = test_func()
        results.append((test_name, result))
    
    # Only run mini test if API key is available
    if results[3][1]:  # API key test passed
        print("\n### Mini Pipeline Test ###")
        result = run_mini_test()
        results.append(("Mini Pipeline Test", result))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nYou can now run:")
        print("  python Orchestrator_v3.py sample/example.txt --preset balanced")
        print("  python app_v3.py  # For web interface")
        print("  python hyperparameter_testing.py --test-type quick")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
