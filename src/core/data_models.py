# core/data_models.py

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PaperSections:
    """논문 섹션 데이터 클래스"""
    introduction: str = ""
    related_work: str = ""
    method: str = ""
    experiments: str = ""
    discussion: str = ""
    conclusion: str = ""

@dataclass
class AgentResult:
    """Agent 분석 결과 데이터 클래스"""
    agent_name: str
    scores: Dict[str, float]
    findings: List[str]
    suggestions: List[str]
    analysis_details: Dict
