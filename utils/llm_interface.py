# utils/llm_interface.py

import openai
import anthropic
from typing import Dict, Optional, Union
import json
import os
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """LLM 인터페이스 추상 클래스"""
    
    @abstractmethod
    def call(self, prompt: str, **kwargs) -> str:
        """LLM API 호출"""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict:
        """응답 파싱"""
        pass

class OpenAIInterface(LLMInterface):
    """OpenAI GPT 인터페이스"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        self.model = model
    
    def call(self, prompt: str, **kwargs) -> str:
        """GPT API 호출"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 논문 분석 전문가입니다. 정확하고 구체적인 분석을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.1),
                max_tokens=kwargs.get("max_tokens", 2000)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API 호출 실패: {e}")
            return ""
    
    def parse_response(self, response: str) -> Dict:
        """JSON 응답 파싱"""
        try:
            # JSON 블록 찾기
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # JSON이 없으면 텍스트 파싱
                return self._parse_text_response(response)
                
        except json.JSONDecodeError:
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict:
        """텍스트 응답을 구조화된 데이터로 파싱"""
        lines = response.split('\n')
        result = {
            "scores": {},
            "findings": [],
            "suggestions": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 섹션 구분
            if "점수" in line or "score" in line.lower():
                current_section = "scores"
            elif "발견" in line or "finding" in line.lower():
                current_section = "findings"
            elif "제안" in line or "suggestion" in line.lower():
                current_section = "suggestions"
            elif line.startswith('-') or line.startswith('•'):
                # 항목 추가
                item = line[1:].strip()
                if current_section == "findings":
                    result["findings"].append(item)
                elif current_section == "suggestions":
                    result["suggestions"].append(item)
            elif ':' in line and current_section == "scores":
                # 점수 파싱
                try:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    # 점수 추출 (⭐ 또는 숫자)
                    if '⭐' in value:
                        score = value.count('⭐')
                    else:
                        import re
                        numbers = re.findall(r'\d+\.?\d*', value)
                        score = float(numbers[0]) if numbers else 3.0
                    
                    result["scores"][key] = score
                except:
                    continue
        
        return result

class AnthropicInterface(LLMInterface):
    """Anthropic Claude 인터페이스"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = model
    
    def call(self, prompt: str, **kwargs) -> str:
        """Claude API 호출"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 2000),
                temperature=kwargs.get("temperature", 0.1),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Anthropic API 호출 실패: {e}")
            return ""
    
    def parse_response(self, response: str) -> Dict:
        """Claude 응답 파싱 (OpenAI와 동일한 방식)"""
        return OpenAIInterface.parse_response(self, response)

class LLMFactory:
    """LLM 인터페이스 팩토리"""
    
    @staticmethod
    def create_llm(provider: str = "openai", **kwargs) -> LLMInterface:
        """LLM 인터페이스 생성"""
        if provider.lower() == "openai":
            return OpenAIInterface(**kwargs)
        elif provider.lower() == "anthropic":
            return AnthropicInterface(**kwargs)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")

class MockLLMInterface(LLMInterface):
    """테스트용 Mock LLM 인터페이스"""
    
    def call(self, prompt: str, **kwargs) -> str:
        """Mock 응답 반환"""
        return """
        {
            "scores": {
                "문제 정의 명확성": 4.2,
                "기존 기술 한계 설명": 3.8,
                "아이디어 중요성": 4.0,
                "기존 연구와 차별성": 3.5
            },
            "findings": [
                "문제 정의가 비교적 명확하나 구체적 예시 부족",
                "기존 기술 한계 설명에서 정량적 근거 필요",
                "차별점이 추상적으로 표현됨"
            ],
            "suggestions": [
                "구체적 사례나 수치를 통한 문제 정의 보강 필요",
                "차별점을 기능적, 성능적 측면에서 구체화",
                "정량적 근거를 통한 한계 설명 강화"
            ]
        }
        """
    
    def parse_response(self, response: str) -> Dict:
        """Mock 응답 파싱"""
        try:
            return json.loads(response.strip())
        except:
            return {
                "scores": {"테스트": 4.0},
                "findings": ["Mock 분석 결과"],
                "suggestions": ["Mock 개선 제안"]
            }

# 사용 예시
def test_llm_interfaces():
    """LLM 인터페이스 테스트"""
    
    # Mock LLM으로 테스트
    mock_llm = MockLLMInterface()
    
    test_prompt = """
    다음 논문 섹션을 USENIX 기준으로 분석해주세요:
    
    === INTRODUCTION ===
    본 연구는 자연어 처리에서 중요한 문제를 다룹니다...
    
    점수와 개선 제안을 JSON 형식으로 제공해주세요.
    """
    
    response = mock_llm.call(test_prompt)
    result = mock_llm.parse_response(response)
    
    print("=== LLM 테스트 결과 ===")
    print(f"점수: {result['scores']}")
    print(f"발견사항: {result['findings']}")
    print(f"제안사항: {result['suggestions']}")
    
    return result

if __name__ == "__main__":
    test_llm_interfaces()
