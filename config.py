# config.py - 설정 관리

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class TreeLLMConfig:
    """TreeLLM 시스템 설정"""
    
    # LLM 설정
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    default_model: str = "gpt-4"
    max_tokens_per_request: int = 2000
    temperature: float = 0.1
    enable_mock_mode: bool = False
    
    # 파일 처리 설정
    max_pdf_size_mb: int = 10
    temp_file_cleanup: bool = True
    max_related_papers: int = 10
    
    # 웹 인터페이스 설정
    streamlit_server_port: int = 8501
    streamlit_server_address: str = "localhost"
    
    # 로깅 설정
    log_level: str = "INFO"
    log_file: str = "logs/treellm.log"
    enable_agent_logging: bool = True
    
    def __post_init__(self):
        """환경 변수에서 설정 로드"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", self.anthropic_api_key)
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", self.default_llm_provider)
        self.default_model = os.getenv("DEFAULT_MODEL", self.default_model)
        
        # 숫자 타입 환경 변수 처리
        self.max_tokens_per_request = int(os.getenv("MAX_TOKENS_PER_REQUEST", self.max_tokens_per_request))
        self.temperature = float(os.getenv("TEMPERATURE", self.temperature))
        self.max_pdf_size_mb = int(os.getenv("MAX_PDF_SIZE_MB", self.max_pdf_size_mb))
        self.max_related_papers = int(os.getenv("MAX_RELATED_PAPERS", self.max_related_papers))
        self.streamlit_server_port = int(os.getenv("STREAMLIT_SERVER_PORT", self.streamlit_server_port))
        
        # 불린 타입 환경 변수 처리
        self.enable_mock_mode = os.getenv("ENABLE_MOCK_MODE", "false").lower() == "true"
        self.temp_file_cleanup = os.getenv("TEMP_FILE_CLEANUP", "true").lower() == "true"
        self.enable_agent_logging = os.getenv("ENABLE_AGENT_LOGGING", "true").lower() == "true"
        
        # 문자열 타입 환경 변수 처리
        self.streamlit_server_address = os.getenv("STREAMLIT_SERVER_ADDRESS", self.streamlit_server_address)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("LOG_FILE", self.log_file)
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        if not self.enable_mock_mode:
            if not self.openai_api_key and not self.anthropic_api_key:
                print("❌ API 키가 설정되지 않았습니다. OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 설정해주세요.")
                return False
        
        if self.default_llm_provider not in ["openai", "anthropic"]:
            print(f"❌ 지원하지 않는 LLM 제공자: {self.default_llm_provider}")
            return False
        
        if self.max_tokens_per_request <= 0:
            print(f"❌ 잘못된 max_tokens_per_request 값: {self.max_tokens_per_request}")
            return False
        
        return True
    
    def print_config(self):
        """현재 설정 출력"""
        print("🔧 TreeLLM 설정 정보")
        print("=" * 30)
        print(f"LLM 제공자: {self.default_llm_provider}")
        print(f"모델: {self.default_model}")
        print(f"최대 토큰: {self.max_tokens_per_request:,}")
        print(f"Temperature: {self.temperature}")
        print(f"Mock 모드: {'✅' if self.enable_mock_mode else '❌'}")
        print(f"최대 PDF 크기: {self.max_pdf_size_mb}MB")
        print(f"최대 관련 논문: {self.max_related_papers}편")
        print(f"로그 레벨: {self.log_level}")
        
        # API 키 상태 (보안상 일부만 표시)
        if self.openai_api_key:
            masked_key = self.openai_api_key[:8] + "..." + self.openai_api_key[-4:]
            print(f"OpenAI API: {masked_key}")
        
        if self.anthropic_api_key:
            masked_key = self.anthropic_api_key[:8] + "..." + self.anthropic_api_key[-4:]
            print(f"Anthropic API: {masked_key}")

# 전역 설정 인스턴스
config = TreeLLMConfig()

def load_config() -> TreeLLMConfig:
    """설정 로드 및 검증"""
    global config
    
    if not config.validate():
        print("\n💡 설정 해결 방법:")
        print("1. .env 파일을 생성하고 API 키를 설정하세요")
        print("2. 또는 환경 변수를 직접 설정하세요:")
        print("   export OPENAI_API_KEY='your-api-key'")
        print("3. 테스트용으로는 ENABLE_MOCK_MODE=true를 설정하세요")
        
        return None
    
    return config

if __name__ == "__main__":
    # 설정 테스트
    config = load_config()
    if config:
        config.print_config()
    else:
        print("❌ 설정 로드 실패")
