# main_app.py
"""
최적화된 메인 Streamlit 애플리케이션
모듈화된 구조로 UI, 파일 생성, 통계 등을 분리
"""

import streamlit as st
import random
from datetime import datetime

# 로컬 모듈 import
from config import Config
from utils import check_azure_config
from ui_components import UIComponents
from file_manager import FileManager
from question_generator import BAQuestionGenerator
from visual_generator import EnhancedBAQuestionGenerator

# 페이지 설정
st.set_page_config(
    page_title="BA 문제 생성기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_visual_question_demo():
    """시각적 문제 생성 데모"""
    st.header("🎨 시각적 요소 포함 문제 생성 데모")
    
    visual_gen = EnhancedBAQuestionGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 설정")
        template_options = {
            'erd_analysis': 'ERD 분석 문제',
            'table_normalization': '테이블 정규화 문제', 
            'uml_design': 'UML 클래스 설계 문제'
        }
        
        selected_template = st.selectbox(
            "문제 유형 선택",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x]
        )
        
        difficulty = st.selectbox("난이도", ["하", "중", "상"], index=1)
        
        if st.button("🎨 시각적 문제 생성", type="primary"):
            question = visual_gen.generate_visual_question(selected_template, difficulty)
            st.session_state['demo_question'] = question
    
    with col2:
        st.subheader("📋 생성된 문제")
        if 'demo_question' in st.session_state:
            UIComponents.display_visual_question(st.session_state['demo_question'], 0)
        else:
            st.info("왼쪽에서 문제를 생성해보세요!")

def calculate_question_distribution(settings: dict) -> list:
    """문제 유형별 분배 계산"""
    total_questions = settings['total_questions']
    
    # 유형별 개수 계산
    mc_count = int(total_questions * settings['multiple_choice_ratio'] / 100)
    sa_count = int(total_questions * settings['short_answer_ratio'] / 100)
    essay_count = total_questions - mc_count - sa_count
    
    question_distribution = []
    
    for q_type, count in [("선다형", mc_count), ("단답형", sa_count), ("서술형", essay_count)]:
        if count > 0:
            # 난이도별 분배
            easy_count = int(count * settings['easy_ratio'] / 100)
            medium_count = int(count * settings['medium_ratio'] / 100)
            hard_count = count - easy_count - medium_count
            
            for difficulty, diff_count in zip(["하", "중", "상"], [easy_count, medium_count, hard_count]):
                for _ in range(diff_count):
                    subject = random.choice(Config.SUBJECT_AREAS)
                    question_distribution.append((q_type, subject, difficulty))
    
    return question_distribution

def generate_questions_with_progress(generator, question_distribution, visual_ratio):
    """진행률과 함께 문제 생성"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    questions = []
    visual_generated = 0
    
    for i, (q_type, subject, difficulty) in enumerate(question_distribution):
        progress = (i + 1) / len(question_distribution)
        progress_bar.progress(progress)
        
        # Enhanced 버전으로 문제 생성 (시각적 요소 포함 가능)
        question = generator.generate_single_question_enhanced(q_type, subject, difficulty)
        questions.append(question)
        
        # 시각적 문제 카운트
        if question.get('visual_image'):
            visual_generated += 1
        
        status_text.text(f"문제 생성 중... ({i + 1}/{len(question_distribution)}) - {q_type}, {difficulty}")
        
        # 중간 결과 표시
        if (i + 1) % 10 == 0:
            st.info(f"✅ {i + 1}개 문제 생성 완료 (시각적 문제: {visual_generated}개)")
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ 문제 생성 완료! (총 {len(questions)}개, 시각적 문제: {visual_generated}개)")
    
    return questions

def display_question_preview(questions):
    """문제 미리보기 표시"""
    st.markdown("---")
    st.header("👀 생성된 문제 미리보기")
    
    # 문제 유형별 탭
    tabs = st.tabs(["전체", "선다형", "단답형", "서술형", "시각적 문제"])
    
    with tabs[0]:  # 전체
        for i, question in enumerate(questions[:10]):  # 처음 10개만 표시
            if question.get('visual_image'):
                UIComponents.display_visual_question(question, i)
            else:
                UIComponents.display_question(question, i)
        
        if len(questions) > 10:
            st.info(f"처음 10개 문제만 표시됩니다. 전체 {len(questions)}개 문제는 다운로드하여 확인하세요.")
    
    for tab_idx, q_type in enumerate(["선다형", "단답형", "서술형"], 1):
        with tabs[tab_idx]:
            type_questions = [q for q in questions if q.get('question_type') == q_type]
            
            if type_questions:
                for i, question in enumerate(type_questions[:5]):  # 타입별로 5개씩 표시
                    if question.get('visual_image'):
                        UIComponents.display_visual_question(question, i)
                    else:
                        UIComponents.display_question(question, i)
                
                if len(type_questions) > 5:
                    st.info(f"{q_type} 문제 중 처음 5개만 표시됩니다. (총 {len(type_questions)}개)")
            else:
                st.write(f"{q_type} 문제가 없습니다.")
    
    # 시각적 문제만 모아서 보기
    with tabs[4]:  # 시각적 문제
        visual_questions = [q for q in questions if q.get('visual_image')]
        
        if visual_questions:
            st.info(f"총 {len(visual_questions)}개의 시각적 문제가 생성되었습니다.")
            
            for i, question in enumerate(visual_questions[:5]):  # 시각적 문제 5개만 표시
                UIComponents.display_visual_question(question, i)
            
            if len(visual_questions) > 5:
                st.info(f"처음 5개 시각적 문제만 표시됩니다. (총 {len(visual_questions)}개)")
        else:
            st.write("생성된 시각적 문제가 없습니다.")

def display_download_section(questions):
    """다운로드 섹션 표시"""
    st.markdown("---")
    st.header("💾 결과 다운로드")
    
    file_manager = FileManager()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # ZIP 파일 다운로드 (전체)
        zip_data = file_manager.create_download_zip(questions)
        st.download_button(
            label="📦 전체 파일 다운로드 (ZIP)",
            data=zip_data,
            file_name=file_manager.get_timestamp_filename("BA_questions", "zip"),
            mime="application/zip",
            help="PDF, JSON, Excel, 통계 파일 모두 포함"
        )
    
    with col2:
        # PDF 파일 다운로드 (시각적 요소 포함)
        pdf_data = file_manager.pdf_generator.create_pdf_document_with_images(questions)
        if pdf_data:
            st.download_button(
                label="📄 PDF 문제집 다운로드",
                data=pdf_data,
                file_name=file_manager.get_timestamp_filename("BA_questions", "pdf"),
                mime="application/pdf",
                help="시각적 요소가 포함된 출력용 PDF 문제집"
            )
        else:
            st.error("PDF 생성에 실패했습니다.")
    
    with col3:
        # JSON 파일 다운로드
        json_data = file_manager.create_json_file(questions)
        st.download_button(
            label="📊 JSON 데이터 다운로드",
            data=json_data.encode('utf-8'),
            file_name=file_manager.get_timestamp_filename("BA_questions", "json"),
            mime="application/json",
            help="데이터 처리용 JSON 파일"
        )

def main():
    """메인 Streamlit 앱"""
    
    # 제목과 설명
    st.title("📚 Business Application 모델링 문제 생성기")
    st.markdown("### 📷 Azure OpenAI + 🎨 시각적 요소 지원")
    st.markdown("---")
    
    # 메뉴 탭
    tab1, tab2 = st.tabs(["📝 문제 생성", "🎨 시각적 문제 데모"])
    
    with tab2:
        create_visual_question_demo()
    
    with tab1:
        # Azure OpenAI 설정 상태 표시
        UIComponents.display_azure_status()
        
        st.write("**Source PDF를 업로드하고 Azure OpenAI를 활용해 텍스트 + 시각적 요소가 포함된 고품질 문제를 생성해보세요!**")
        
        # 사이드바 설정
        settings = UIComponents.display_sidebar_settings()
        
        # PDF 파일 업로드
        st.header("📄 Source PDF 업로드")
        uploaded_file = st.file_uploader(
            "학습자료 PDF를 업로드하세요",
            type=['pdf'],
            help="Business Application 모델링 관련 학습자료를 업로드하세요"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ 파일 업로드 완료: {uploaded_file.name}")
            
            # PDF 내용 미리보기
            with st.expander("📖 PDF 내용 미리보기"):
                generator = BAQuestionGenerator()
                
                # 시각적 문제 비율 설정
                generator.visual_question_ratio = settings['visual_ratio'] / 100
                
                content = generator.extract_pdf_content(uploaded_file)
                if content:
                    st.text_area(
                        "추출된 내용 (처음 1000자)",
                        content[:1000] + "..." if len(content) > 1000 else content,
                        height=200
                    )
                else:
                    st.error("PDF 내용을 추출할 수 없습니다.")
        
        st.markdown("---")
        
        # Azure OpenAI 설정 유효성 검사
        azure_status = check_azure_config()
        api_configured = azure_status['azure_configured']
        
        # 문제 생성 버튼
        if st.button("🚀 문제 생성 시작", type="primary", disabled=not uploaded_file or not api_configured):
            if not api_configured:
                st.error("❌ Azure OpenAI가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            elif not uploaded_file:
                st.error("❌ PDF 파일을 업로드해주세요.")
            else:
                # 문제 생성 진행
                generator = BAQuestionGenerator()
                
                # 시각적 문제 비율 설정
                generator.visual_question_ratio = settings['visual_ratio'] / 100
                
                # Azure OpenAI 연결 확인
                if not generator.api_configured:
                    st.error("❌ Azure OpenAI 연결에 실패했습니다. 설정을 확인해주세요.")
                    return
                
                # 문제 유형별 분배 계산
                question_distribution = calculate_question_distribution(settings)
                
                # 문제 생성
                questions = generate_questions_with_progress(generator, question_distribution, settings['visual_ratio'])
                
                # 세션 상태에 결과 저장
                st.session_state['questions'] = questions
                st.session_state['generation_complete'] = True
                
                st.success(f"🎉 총 {len(questions)}개 문제 생성 완료!")
        
        # 결과 표시
        if 'questions' in st.session_state and st.session_state.get('generation_complete'):
            questions = st.session_state['questions']
            
            st.markdown("---")
            st.header("📊 생성 결과")
            
            # 통계 차트 표시
            UIComponents.display_statistics_charts(questions)
            
            # 다운로드 섹션
            display_download_section(questions)
            
            # 문제 미리보기
            display_question_preview(questions)
            
            # 재생성 버튼
            st.markdown("---")
            if st.button("🔄 새로운 문제 생성", type="secondary"):
                if 'questions' in st.session_state:
                    del st.session_state['questions']
                if 'generation_complete' in st.session_state:
                    del st.session_state['generation_complete']
                st.rerun()

if __name__ == "__main__":
    # 필요한 라이브러리 설치 안내
    try:
        import matplotlib
        from PIL import Image
    except ImportError:
        st.error("""
        📦 필수 라이브러리가 설치되지 않았습니다.
        
        다음 명령어로 설치해주세요:
        ```
        pip install matplotlib pillow
        ```
        """)
        st.stop()
    
    main()