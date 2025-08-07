#!/usr/bin/env python3
"""
TreeLLM Extended API 테스트 스크립트
=====================================
새로운 엔드포인트들을 테스트합니다.
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:5001/api"
SESSION_ID = "test-session-123"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"X-Session-ID": SESSION_ID})
    
    def test_health(self):
        """서버 상태 확인"""
        print("\n1. Health Check")
        print("-" * 50)
        
        response = self.session.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Version: {data.get('version')}")
        print(f"API Key Configured: {data.get('api_key_configured')}")
        print(f"Active Jobs: {data.get('active_jobs')}")
        
        return response.status_code == 200
    
    def test_presets(self):
        """프리셋 목록 조회"""
        print("\n2. Get Presets")
        print("-" * 50)
        
        response = self.session.get(f"{BASE_URL}/presets")
        presets = response.json()
        
        for name, info in presets.items():
            print(f"\n[{name}]")
            print(f"  Description: {info['description']}")
            print(f"  Model: {info['model']}")
            print(f"  Temperature: {info['temperature']}")
            print(f"  Est. Cost/1k chars: ${info['estimated_cost_per_1k_chars']:.4f}")
        
        return response.status_code == 200
    
    def test_cost_estimation(self):
        """비용 예측"""
        print("\n3. Cost Estimation")
        print("-" * 50)
        
        data = {
            "text_length": 10000,
            "preset": "balanced"
        }
        
        response = self.session.post(f"{BASE_URL}/estimate-cost", json=data)
        result = response.json()
        
        print(f"Text Length: {result['text_length']:,} chars")
        print(f"Model: {result['model']}")
        print(f"\nCosts by Module:")
        
        for module, cost in result['costs_by_module'].items():
            print(f"  {module:<15}: ${cost:.4f}")
        
        print(f"\nTotal Cost: ${result['total_cost']:.4f} {result['currency']}")
        
        return response.status_code == 200
    
    def test_split_module(self):
        """Split 모듈 테스트 (API 키 불필요)"""
        print("\n4. Split Module Test")
        print("-" * 50)
        
        sample_text = """
# Introduction
This is a test document for the TreeLLM system.

# Method
We use a multi-stage pipeline to process documents.

# Results
The system achieves high accuracy in document analysis.

# Conclusion
TreeLLM provides an effective solution for paper analysis.
        """
        
        data = {"text": sample_text}
        response = self.session.post(f"{BASE_URL}/modules/split", json=data)
        result = response.json()
        
        if result.get('success'):
            print(f"Success: {result['success']}")
            print(f"Number of sections: {result['num_sections']}")
            print(f"Sections: {', '.join(result['section_names'])}")
            print("\nSection lengths:")
            for name, length in result['section_lengths'].items():
                print(f"  {name}: {length} chars")
        else:
            print(f"Error: {result.get('error')}")
        
        return response.status_code == 200
    
    def test_mock_modules(self):
        """Mock 모드로 모듈 테스트"""
        print("\n5. Mock Module Tests")
        print("-" * 50)
        
        modules = ['build', 'audit', 'edit1', 'global_check', 'edit2']
        
        for module in modules:
            data = {
                "module": module,
                "mock": True,
                "text": "Test text"
            }
            
            response = self.session.post(f"{BASE_URL}/modules/test", json=data)
            result = response.json()
            
            print(f"\n{module.upper()}:")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Mock: {result.get('mock', False)}")
            
            if result.get('warning'):
                print(f"  Warning: {result['warning']}")
        
        return True
    
    def test_file_upload(self):
        """파일 업로드 테스트"""
        print("\n6. File Upload Test")
        print("-" * 50)
        
        # 테스트 파일 생성
        test_file = Path("test_upload.txt")
        test_file.write_text("This is a test file for upload.")
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = self.session.post(f"{BASE_URL}/upload", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Upload Success: {result['success']}")
                print(f"File ID: {result['file']['id']}")
                print(f"Filename: {result['file']['filename']}")
                print(f"Size: {result['file']['size']} bytes")
                print(f"Text Length: {result['file']['text_length']} chars")
                return result['file']['id']
            else:
                print(f"Upload failed: {response.status_code}")
                return None
                
        finally:
            test_file.unlink()  # 테스트 파일 삭제
    
    def test_pipeline_async(self, file_id=None):
        """비동기 파이프라인 테스트"""
        print("\n7. Async Pipeline Test")
        print("-" * 50)
        
        data = {
            "preset": "fast",
            "config": {"model": {"temperature": 0.1}}
        }
        
        if file_id:
            data["file_id"] = file_id
        else:
            data["text"] = "This is a test document for pipeline processing."
        
        # 파이프라인 시작
        response = self.session.post(f"{BASE_URL}/pipeline/start", json=data)
        
        if response.status_code != 200:
            print(f"Failed to start pipeline: {response.json()}")
            return False
        
        result = response.json()
        job_id = result['job_id']
        
        print(f"Job ID: {job_id}")
        print(f"Status: {result['status']}")
        print(f"Estimated Time: {result['estimated_time']}s")
        print(f"Estimated Cost: ${result['estimated_cost']:.4f}")
        
        # 상태 모니터링 (최대 10초)
        print("\nMonitoring job status...")
        for i in range(10):
            time.sleep(1)
            status_response = self.session.get(f"{BASE_URL}/pipeline/status/{job_id}")
            status = status_response.json()
            
            print(f"  [{i+1}s] Status: {status['status']}, Progress: {status['progress']}%", end="")
            if status['current_step']:
                print(f", Step: {status['current_step']}")
            else:
                print()
            
            if status['status'] in ['completed', 'failed']:
                break
        
        return job_id
    
    def test_list_jobs(self):
        """작업 목록 조회"""
        print("\n8. List Jobs")
        print("-" * 50)
        
        response = self.session.get(f"{BASE_URL}/jobs?per_page=5")
        result = response.json()
        
        print(f"Total Jobs: {result['total']}")
        print(f"Page: {result['page']}/{result['pages']}")
        print("\nRecent Jobs:")
        
        for job in result['jobs'][:5]:
            print(f"\n  ID: {job['id']}")
            print(f"  Type: {job['type']}")
            print(f"  Status: {job['status']}")
            print(f"  Created: {job['created_at']}")
            print(f"  Progress: {job['progress']}%")
        
        return response.status_code == 200
    
    def test_cache_management(self):
        """캐시 관리 테스트"""
        print("\n9. Cache Management")
        print("-" * 50)
        
        # 캐시 상태 조회
        response = self.session.get(f"{BASE_URL}/cache")
        cache_info = response.json()
        
        print(f"Cache Files: {cache_info['files']}")
        print(f"Cache Size: {cache_info['size']:,} bytes")
        
        # 오래된 캐시 정리
        response = self.session.delete(f"{BASE_URL}/cache?max_age_hours=1")
        result = response.json()
        
        print(f"\nCache Cleanup:")
        print(f"  {result['message']}")
        
        return True
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("TreeLLM Extended API Test Suite")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health),
            ("Presets", self.test_presets),
            ("Cost Estimation", self.test_cost_estimation),
            ("Split Module", self.test_split_module),
            ("Mock Modules", self.test_mock_modules),
            ("File Upload", self.test_file_upload),
            ("Cache Management", self.test_cache_management),
            ("List Jobs", self.test_list_jobs),
        ]
        
        results = []
        file_id = None
        
        for name, test_func in tests:
            try:
                if name == "File Upload":
                    file_id = test_func()
                    success = file_id is not None
                else:
                    success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"\nError in {name}: {str(e)}")
                results.append((name, False))
        
        # Pipeline 테스트는 파일 업로드 결과 사용
        try:
            job_id = self.test_pipeline_async(file_id)
            results.append(("Async Pipeline", job_id is not None))
        except Exception as e:
            print(f"\nError in Async Pipeline: {str(e)}")
            results.append(("Async Pipeline", False))
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{name:<20}: {status}")
        
        success_count = sum(1 for _, success in results if success)
        print(f"\nTotal: {success_count}/{len(results)} tests passed")
        
        return success_count == len(results)


if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server is not running!")
        print("Please start the server first:")
        print("  python app_extended.py")
        sys.exit(1)
    
    # 테스트 실행
    tester = APITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
