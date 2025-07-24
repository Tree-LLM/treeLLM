# utils/pdf_processor.py

import PyPDF2
import pdfplumber
from typing import Dict, Optional
import re

class PDFProcessor:
    """PDF 파일 처리 유틸리티"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"PDF 텍스트 추출 실패: {e}")
            return ""
    
    @staticmethod
    def extract_sections_from_pdf(pdf_path: str) -> Dict[str, str]:
        """PDF에서 논문 섹션별로 텍스트 추출"""
        text = PDFProcessor.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {}
        
        # 섹션 헤더 패턴 정의
        section_patterns = {
            'introduction': r'(?i)(?:1\.?\s*)?introduction',
            'related_work': r'(?i)(?:2\.?\s*)?(?:related\s*work|background)',
            'method': r'(?i)(?:3\.?\s*)?(?:method|methodology|approach)',
            'experiments': r'(?i)(?:4\.?\s*)?(?:experiment|evaluation|results)',
            'discussion': r'(?i)(?:5\.?\s*)?(?:discussion|analysis)',
            'conclusion': r'(?i)(?:6\.?\s*)?(?:conclusion|conclusions)'
        }
        
        sections = {}
        
        # 각 섹션별로 텍스트 추출
        for section_name, pattern in section_patterns.items():
            section_text = PDFProcessor._extract_section_text(text, pattern)
            sections[section_name] = section_text
        
        return sections
    
    @staticmethod
    def _extract_section_text(full_text: str, section_pattern: str) -> str:
        """특정 섹션의 텍스트 추출"""
        # 섹션 시작점 찾기
        match = re.search(section_pattern, full_text, re.IGNORECASE)
        if not match:
            return ""
        
        start_pos = match.end()
        
        # 다음 섹션까지의 텍스트 추출
        next_section_patterns = [
            r'(?i)(?:\d+\.?\s*)?(?:introduction|related\s*work|background|method|experiment|discussion|conclusion|references|acknowledgment)',
        ]
        
        end_pos = len(full_text)
        for pattern in next_section_patterns:
            next_match = re.search(pattern, full_text[start_pos:], re.IGNORECASE)
            if next_match:
                end_pos = start_pos + next_match.start()
                break
        
        section_text = full_text[start_pos:end_pos].strip()
        
        # 텍스트 정리
        section_text = re.sub(r'\s+', ' ', section_text)  # 공백 정리
        section_text = re.sub(r'\n+', '\n', section_text)  # 줄바꿈 정리
        
        return section_text[:2000]  # 최대 2000자로 제한
    
    @staticmethod
    def extract_metadata_from_pdf(pdf_path: str) -> Dict:
        """PDF에서 메타데이터 추출"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                    'modification_date': metadata.get('/ModDate', ''),
                    'page_count': len(pdf_reader.pages)
                }
        except Exception as e:
            print(f"PDF 메타데이터 추출 실패: {e}")
            return {}

class RelatedPaperProcessor:
    """관련 논문 처리 전용 클래스"""
    
    @staticmethod
    def process_uploaded_papers(pdf_files: list) -> list:
        """업로드된 PDF들을 처리하여 논문 정보 추출"""
        related_papers = []
        
        for pdf_file in pdf_files:
            try:
                # PDF 텍스트 추출
                text = PDFProcessor.extract_text_from_pdf(pdf_file)
                
                # 메타데이터 추출
                metadata = PDFProcessor.extract_metadata_from_pdf(pdf_file)
                
                # 핵심 정보 추출
                paper_info = {
                    "title": RelatedPaperProcessor._extract_title(text, metadata),
                    "authors": RelatedPaperProcessor._extract_authors(text),
                    "year": RelatedPaperProcessor._extract_year(text),
                    "abstract": RelatedPaperProcessor._extract_abstract(text),
                    "method": RelatedPaperProcessor._extract_method_summary(text),
                    "contributions": RelatedPaperProcessor._extract_contributions(text),
                    "file_path": pdf_file
                }
                
                related_papers.append(paper_info)
                
            except Exception as e:
                print(f"논문 처리 실패 ({pdf_file}): {e}")
                continue
        
        return related_papers
    
    @staticmethod
    def _extract_title(text: str, metadata: Dict) -> str:
        """제목 추출"""
        # 메타데이터에서 먼저 시도
        if metadata.get('title'):
            return metadata['title']
        
        # 텍스트에서 추출 시도
        lines = text.split('\n')[:10]  # 첫 10줄에서 찾기
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:  # 적절한 길이
                if not re.match(r'^\d+', line):  # 번호로 시작하지 않음
                    return line
        
        return "Unknown Title"
    
    @staticmethod
    def _extract_authors(text: str) -> list:
        """저자 추출"""
        # 일반적인 저자 패턴 찾기
        author_patterns = [
            r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)',
            r'Authors?:\s*([^\n]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text)
            if match:
                authors_str = match.group(1)
                authors = [author.strip() for author in authors_str.split(',')]
                return authors[:5]  # 최대 5명까지
        
        return ["Unknown Author"]
    
    @staticmethod
    def _extract_year(text: str) -> Optional[int]:
        """발행 연도 추출"""
        # 2000-2030 범위의 연도 찾기
        year_pattern = r'(20[0-2][0-9])'
        matches = re.findall(year_pattern, text[:1000])  # 첫 1000자에서
        
        if matches:
            return int(matches[0])
        
        return None
    
    @staticmethod
    def _extract_abstract(text: str) -> str:
        """초록 추출"""
        abstract_pattern = r'(?i)abstract\s*[:\-]?\s*(.*?)(?=\n\s*(?:keywords|introduction|\d+\.))'
        match = re.search(abstract_pattern, text, re.DOTALL)
        
        if match:
            abstract = match.group(1).strip()
            abstract = re.sub(r'\s+', ' ', abstract)  # 공백 정리
            return abstract[:500]  # 500자로 제한
        
        return ""
    
    @staticmethod
    def _extract_method_summary(text: str) -> str:
        """방법론 요약 추출"""
        method_patterns = [
            r'(?i)(?:method|approach|methodology)\s*[:\-]?\s*(.*?)(?=\n\s*(?:\d+\.|experiment|evaluation))',
            r'(?i)our\s+(?:approach|method)\s+(.*?)(?=\.|we|the)'
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                method = match.group(1).strip()
                method = re.sub(r'\s+', ' ', method)
                return method[:300]
        
        return ""
    
    @staticmethod
    def _extract_contributions(text: str) -> list:
        """기여도 추출"""
        contribution_patterns = [
            r'(?i)our\s+(?:main\s+)?contributions?\s+(?:are|include)\s*(.*?)(?=\n\s*\d+\.)',
            r'(?i)contributions?\s*[:\-]\s*(.*?)(?=\n\s*(?:\d+\.|the))',
            r'(?i)we\s+(?:propose|present|introduce)\s+(.*?)(?=\.|,)'
        ]
        
        contributions = []
        for pattern in contribution_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                contrib = match.strip()
                if len(contrib) > 20:  # 의미있는 길이
                    contributions.append(contrib[:200])
        
        return contributions[:3]  # 최대 3개
