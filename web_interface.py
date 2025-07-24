# web_interface.py - Streamlit 웹 인터페이스

import streamlit as st
import sys
import os
sys.path.append('src')

from src.core import PaperSections
from treellm_system import TreeLLMSystem
from utils.pdf_processor import PDFProcessor, RelatedPaperProcessor
import json

def init_session_state():
    """세션 상태 초기화"""
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'treellm' not in st.session_state:
        st.session_state.treellm = TreeLLMSystem()

def display_header():
    """헤더 표시"""
    st.set_page_config(
        page_title="TreeLLM - AI Paper Analyzer",
        page_icon="🌳",
        layout="wide"
    )
    
    st.title("🌳 TreeLLM")
    st.subtitle("AI Agent 기반 논문 분석 시스템")
    st.markdown("---")

def paper_input_section():
    """논문 입력 섹션"""
    st.header("📄 논문 입력")
    
    input_method = st.radio(
        "입력 방식 선택:",
        ["텍스트 직접 입력", "PDF 파일 업로드"]
    )
    
    paper_sections = None
    
    if input_method == "텍스트 직접 입력":
        paper_sections = text_input_interface()
    else:
        paper_sections = pdf_upload_interface()
    
    return paper_sections

def text_input_interface():
    """텍스트 직접 입력 인터페이스"""
    col1, col2 = st.columns(2)
    
    with col1:
        introduction = st.text_area(
            "Introduction",
            height=150,
            placeholder="논문의 Introduction 섹션을 입력하세요..."
        )
        
        method = st.text_area(
            "Method",
            height=150,
            placeholder="Method 섹션을 입력하세요..."
        )
        
        discussion = st.text_area(
            "Discussion",
            height=150,
            placeholder="Discussion 섹션을 입력하세요..."
        )
    
    with col2:
        related_work = st.text_area(
            "Related Work",
            height=150,
            placeholder="Related Work 섹션을 입력하세요..."
        )
        
        experiments = st.text_area(
            "Experiments",
            height=150,
            placeholder="Experiments 섹션을 입력하세요..."
        )
        
        conclusion = st.text_area(
            "Conclusion",
            height=150,
            placeholder="Conclusion 섹션을 입력하세요..."
        )
    
    if any([introduction, related_work, method, experiments, discussion, conclusion]):
        return PaperSections(
            introduction=introduction,
            related_work=related_work,
            method=method,
            experiments=experiments,
            discussion=discussion,
            conclusion=conclusion
        )
    
    return None

def pdf_upload_interface():
    """PDF 업로드 인터페이스"""
    uploaded_file = st.file_uploader(
        "논문 PDF 파일을 업로드하세요",
        type=['pdf'],
        help="PDF에서 자동으로 섹션을 추출합니다"
    )
    
    if uploaded_file is not None:
        with st.spinner("PDF 파일 처리 중..."):
            try:
                # 임시 파일로 저장
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 섹션 추출
                sections_dict = PDFProcessor.extract_sections_from_pdf(temp_path)
                
                # 메타데이터 추출
                metadata = PDFProcessor.extract_metadata_from_pdf(temp_path)
                
                # 임시 파일 삭제
                os.remove(temp_path)
                
                # 결과 표시
                st.success("✅ PDF 처리 완료!")
                
                if metadata.get('title'):
                    st.info(f"📖 제목: {metadata['title']}")
                if metadata.get('page_count'):
                    st.info(f"📄 페이지 수: {metadata['page_count']}")
                
                # 추출된 섹션 미리보기
                with st.expander("추출된 섹션 미리보기"):
                    for section_name, content in sections_dict.items():
                        if content.strip():
                            st.text_area(
                                f"{section_name.title()}",
                                value=content[:200] + "..." if len(content) > 200 else content,
                                height=80,
                                disabled=True
                            )
                
                return PaperSections(**sections_dict)
                
            except Exception as e:
                st.error(f"❌ PDF 처리 실패: {e}")
    
    return None

def related_papers_section():
    """관련 논문 섹션"""
    st.header("📚 관련 논문 비교 (선택사항)")
    
    with st.expander("관련 논문 업로드"):
        st.markdown("""
        관련 논문들을 업로드하면 더 정확한 비교 분석이 가능합니다.
        - 권장: 3-10편의 관련 논문
        - 지원 형식: PDF
        """)
        
        uploaded_papers = st.file_uploader(
            "관련 논문 PDF 파일들",
            type=['pdf'],
            accept_multiple_files=True,
            help="여러 파일을 선택할 수 있습니다"
        )
        
        if uploaded_papers:
            st.success(f"✅ {len(uploaded_papers)}편의 관련 논문 업로드됨")
            
            # 간단한 정보 표시
            for i, paper in enumerate(uploaded_papers, 1):
                st.text(f"{i}. {paper.name}")
            
            return uploaded_papers
    
    return None

def analysis_options_section():
    """분석 옵션 섹션"""
    st.header("🔍 분석 옵션")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**USENIX 기준 검증** (필수)")
        usenix_agents = st.multiselect(
            "USENIX Agent 선택:",
            ["OriginalityAgent", "LessonExtractionAgent", "AssumptionAgent"],
            default=["OriginalityAgent", "LessonExtractionAgent"],
            help="USENIX Guidelines 기준으로 논문을 평가합니다"
        )
    
    with col2:
        st.markdown("**추가 분석 옵션**")
        enable_comparison = st.checkbox(
            "관련 논문 비교 분석", 
            help="업로드된 관련 논문들과 비교합니다"
        )
        
        show_token_usage = st.checkbox(
            "토큰 사용량 표시",
            help="예상 토큰 사용량과 비용을 표시합니다"
        )
    
    return usenix_agents, enable_comparison, show_token_usage

def display_analysis_results(results):
    """분석 결과 표시"""
    st.header("📊 분석 결과")
    
    # 전체 요약
    summary = results['integrated_summary']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 점수", f"{summary['overall_score']:.2f}/5.0")
    with col2:
        st.metric("개선 제안", f"{summary['total_suggestions']}개")
    with col3:
        improvement_count = len(summary['priority_improvements'])
        st.metric("우선 개선", f"{improvement_count}개")
    
    # Agent별 상세 결과
    st.subheader("🤖 Agent별 분석 결과")
    
    for agent_name, result in results['usenix_analysis'].items():
        with st.expander(f"{agent_name} 결과", expanded=True):
            
            # 점수 표시
            st.markdown("**📈 점수**")
            score_cols = st.columns(len(result.scores))
            
            for i, (criterion, score) in enumerate(result.scores.items()):
                with score_cols[i]:
                    # 점수에 따른 색상
                    if score >= 4.0:
                        color = "🟢"
                    elif score >= 3.0:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.metric(
                        criterion,
                        f"{score:.1f}",
                        delta=None,
                        help=f"5점 만점 기준 {color}"
                    )
            
            # 발견사항
            st.markdown("**🔍 주요 발견사항**")
            for finding in result.findings:
                st.write(f"• {finding}")
            
            # 개선 제안
            st.markdown("**💡 개선 제안**")
            for suggestion in result.suggestions:
                st.write(f"• {suggestion}")
    
    # 관련 논문 비교 결과
    if results.get('comparison_analysis'):
        st.subheader("📚 관련 논문 비교 결과")
        comp_result = results['comparison_analysis']
        
        with st.expander("비교 분석 결과", expanded=True):
            # 비교 점수
            st.markdown("**📊 비교 점수**")
            comp_cols = st.columns(len(comp_result.scores))
            
            for i, (criterion, score) in enumerate(comp_result.scores.items()):
                with comp_cols[i]:
                    st.metric(criterion, f"{score:.1f}/5.0")
            
            # 비교 발견사항
            st.markdown("**🔍 비교 분석 발견사항**")
            for finding in comp_result.findings:
                st.write(f"• {finding}")
    
    # 결과 다운로드
    st.subheader("💾 결과 다운로드")
    
    # JSON 형태로 다운로드
    results_json = json.dumps(results, ensure_ascii=False, indent=2, default=str)
    
    st.download_button(
        label="📥 분석 결과 다운로드 (JSON)",
        data=results_json,
        file_name="treellm_analysis_results.json",
        mime="application/json"
    )

def sidebar_info():
    """사이드바 정보"""
    st.sidebar.title("ℹ️ TreeLLM 정보")
    
    st.sidebar.markdown("""
    ### 📋 지원 기능
    - USENIX Guidelines 기준 검증
    - Agent 기반 전문 분석
    - 관련 논문 비교 분석
    - PDF 자동 섹션 추출
    - 결과 다운로드
    
    ### 🤖 사용 가능한 Agent
    - **OriginalityAgent**: 독창성 평가
    - **LessonExtractionAgent**: 교훈 추출
    - **AssumptionAgent**: 가정사항 분석
    
    ### 💡 사용 팁
    1. 논문의 모든 섹션을 입력하세요
    2. 관련 논문을 업로드하면 더 정확합니다
    3. 결과를 JSON으로 저장할 수 있습니다
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**개발팀**: TreeLLM Team")
    st.sidebar.markdown("**버전**: v0.1.0")

def main():
    """메인 웹 인터페이스"""
    init_session_state()
    display_header()
    
    # 1. 논문 입력
    paper_sections = paper_input_section()
    
    # 2. 관련 논문 업로드
    uploaded_papers = related_papers_section()
    
    # 3. 분석 옵션
    selected_agents, enable_comparison, show_token_usage = analysis_options_section()
    
    # 4. 토큰 사용량 표시
    if show_token_usage and paper_sections:
        st.subheader("💰 예상 토큰 사용량")
        token_usage = st.session_state.treellm.get_agent_token_usage()
        
        total_tokens = sum(token_usage[agent] for agent in selected_agents if agent in token_usage)
        estimated_cost = total_tokens * 0.00003  # GPT-4 기준
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("예상 토큰", f"{total_tokens:,}")
        with col2:
            st.metric("예상 비용", f"${estimated_cost:.3f}")
        
        with st.expander("Agent별 토큰 사용량"):
            for agent in selected_agents:
                if agent in token_usage:
                    st.text(f"{agent}: {token_usage[agent]:,} 토큰")
    
    # 5. 분석 실행 버튼
    st.markdown("---")
    
    if st.button("🚀 논문 분석 시작", type="primary", use_container_width=True):
        if not paper_sections:
            st.error("❌ 논문 내용을 입력해주세요.")
            return
        
        if not selected_agents:
            st.error("❌ 최소 하나의 USENIX Agent를 선택해주세요.")
            return
        
        # 분석 실행
        with st.spinner("🔄 논문 분석 중... (1-2분 소요)"):
            try:
                # 관련 논문 처리
                related_papers_data = None
                if uploaded_papers and enable_comparison:
                    # PDF 처리 (실제 구현에서는 RelatedPaperProcessor 사용)
                    related_papers_data = [
                        {"title": paper.name, "year": 2023} 
                        for paper in uploaded_papers
                    ]
                
                # 분석 실행
                results = st.session_state.treellm.analyze_paper(
                    paper_sections=paper_sections,
                    uploaded_papers=related_papers_data,
                    selected_agents=selected_agents
                )
                
                st.session_state.analysis_results = results
                st.success("✅ 분석 완료!")
                
            except Exception as e:
                st.error(f"❌ 분석 중 오류 발생: {e}")
                return
    
    # 6. 결과 표시
    if st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results)

if __name__ == "__main__":
    sidebar_info()
    main()
