# ui_components.py
"""
UI 컴포넌트 모듈
Streamlit UI 관련 함수들
"""

import streamlit as st
import plotly.express as px
from typing import List, Dict, Any

from config import Config
from utils import check_azure_config, generate_statistics

class UIComponents:
    """UI 컴포넌트 클래스"""
    
    @staticmethod
    def display_azure_status():
        """Azure OpenAI 설정 상태 표시"""
        azure_status = check_azure_config()
        
        if not azure_status['env_file_exists']:
            st.warning("⚠️ .env 파일이 없습니다. Azure OpenAI 설정을 확인해주세요.")
            UIComponents.display_config_help()
        else:
            if azure_status['azure_configured']:
                st.success("✅ Azure OpenAI 설정 완료")
                st.info(f"🌐 엔드포인트: {azure_status['endpoint']}")
                st.info(f"🚀 배포 모델: {azure_status['deployment_name']}")
            else:
                st.error("❌ Azure OpenAI 설정이 완전하지 않습니다.")
                missing_vars = [k for k, v in azure_status['configured_vars'].items() if not v]
                st.error(f"누락된 환경변수: {', '.join(missing_vars)}")
    
    @staticmethod
    def display_config_help():
        """Azure OpenAI 설정 도움말 표시"""
        with st.expander("🔧 Azure OpenAI 설정 도움말", expanded=True):
            st.markdown("### Azure OpenAI 설정 방법")
            st.markdown("1. Azure Portal에서 OpenAI 리소스를 생성하세요.")
            st.markdown("2. 모델을 배포하세요 (예: GPT-4, GPT-3.5-turbo).")
            st.markdown("3. 프로젝트 루트에 `.env` 파일을 생성하세요.")
            st.markdown("4. 아래 템플릿을 복사하여 붙여넣고 실제 값으로 변경하세요.")
            
            env_template = Config.get_env_template()
            st.code(env_template, language='bash')
            
            st.download_button(
                label="📄 .env 템플릿 다운로드",
                data=env_template,
                file_name=".env",
                mime="text/plain"
            )
            
            st.markdown("5. 각 값을 실제 Azure OpenAI 설정으로 변경하세요:")
            st.markdown("   - `OPENAI_ENDPOINT`: Azure OpenAI 엔드포인트 URL")
            st.markdown("   - `OPENAI_KEY`: Azure OpenAI API 키")
            st.markdown("   - `CHAT_MODEL3`: 배포된 모델 이름")
            st.markdown("6. 파일을 저장하고 앱을 다시 시작하세요.")
    
    @staticmethod
    def display_sidebar_settings():
        """사이드바 설정 표시"""
        with st.sidebar:
            st.subheader("📝 문제 설정")
            
            total_questions = st.slider(
                "총 문제 수",
                min_value=10,
                max_value=200,
                value=Config.DEFAULT_QUESTION_COUNT,
                step=10
            )
            
            # 문제 유형별 비율 설정
            st.subheader("📊 문제 유형 비율")
            multiple_choice_ratio = st.slider("선다형 (%)", 0, 100, Config.DEFAULT_RATIOS['multiple_choice'])
            short_answer_ratio = st.slider("단답형 (%)", 0, 100, Config.DEFAULT_RATIOS['short_answer'])
            essay_ratio = 100 - multiple_choice_ratio - short_answer_ratio
            st.write(f"서술형: {essay_ratio}%")
            
            # 난이도 비율 설정
            st.subheader("🎯 난이도 비율")
            easy_ratio = st.slider("하 (%)", 0, 100, Config.DEFAULT_DIFFICULTY_RATIOS['easy'])
            medium_ratio = st.slider("중 (%)", 0, 100, Config.DEFAULT_DIFFICULTY_RATIOS['medium'])
            hard_ratio = 100 - easy_ratio - medium_ratio
            st.write(f"상: {hard_ratio}%")
            
            # 시각적 문제 비율 설정
            st.subheader("🎨 시각적 요소 설정")
            visual_ratio = st.slider("시각적 문제 비율 (%)", 0, 100, Config.DEFAULT_VISUAL_RATIO)
            st.caption("데이터 모델링, 프로세스 설계 등에서 ERD, UML, 플로우차트 등을 포함한 문제 생성")
            
            # 디버그 정보 (DEBUG=True일 때만 표시)
            if Config.DEBUG_MODE:
                st.markdown("---")
                st.subheader("🛠 디버그 정보")
                azure_status = check_azure_config()
                st.json({
                    "env_file_exists": azure_status['env_file_exists'],
                    "azure_configured": azure_status['azure_configured'],
                    "configured_vars": azure_status['configured_vars'],
                    "deployment_name": azure_status['deployment_name'],
                    "debug_mode": True
                })
        
        return {
            'total_questions': total_questions,
            'multiple_choice_ratio': multiple_choice_ratio,
            'short_answer_ratio': short_answer_ratio,
            'essay_ratio': essay_ratio,
            'easy_ratio': easy_ratio,
            'medium_ratio': medium_ratio,
            'hard_ratio': hard_ratio,
            'visual_ratio': visual_ratio
        }
    
    @staticmethod
    def display_question(question: Dict[str, Any], index: int):
        """일반 문제 표시"""
        with st.expander(f"📝 문제 {index + 1}: {question.get('title', '제목 없음')}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**유형:** {question.get('question_type', 'N/A')}")
            with col2:
                st.write(f"**난이도:** {question.get('difficulty', 'N/A')}")
            with col3:
                st.write(f"**배점:** {question.get('points', 'N/A')}")
            
            if question.get('scenario'):
                st.write(f"**시나리오:** {question['scenario']}")
            
            st.write(f"**문제:** {question.get('question', 'N/A')}")
            
            if question.get('question_type') == '선다형' and question.get('choices'):
                for choice in question['choices']:
                    st.write(choice)
                st.success(f"**정답:** {question.get('correct_answer', 'N/A')}")
            elif question.get('question_type') == '단답형':
                st.success(f"**정답:** {question.get('correct_answer', 'N/A')}")
                if question.get('alternative_answers'):
                    alt_answers = question['alternative_answers']
                    if isinstance(alt_answers, list):
                        alt_strings = []
                        for item in alt_answers:
                            if isinstance(item, str):
                                alt_strings.append(item)
                            elif isinstance(item, dict):
                                alt_strings.append(str(item.get('answer', item)))
                            else:
                                alt_strings.append(str(item))
                        
                        if alt_strings:
                            st.info(f"**가능한 답:** {', '.join(alt_strings)}")
            elif question.get('question_type') == '서술형':
                st.success(f"**모범답안:** {question.get('model_answer', 'N/A')}")
                if question.get('grading_criteria'):
                    st.info("**채점기준:**")
                    for i, criteria in enumerate(question['grading_criteria'], 1):
                        st.write(f"{i}. {criteria}")
            
            if question.get('explanation'):
                st.write(f"**해설:** {question['explanation']}")
            
            st.caption(f"과목: {question.get('subject_area', 'N/A')}")
    
    @staticmethod
    def display_visual_question(question: Dict[str, Any], index: int):
        """시각적 문제 표시"""
        with st.expander(f"🎨 문제 {index + 1}: {question.get('title', '제목 없음')}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**유형:** {question.get('question_type', 'N/A')}")
                if question.get('visual_type'):
                    st.write(f"**시각 요소:** {question.get('visual_type', 'N/A').upper()}")
            with col2:
                st.write(f"**난이도:** {question.get('difficulty', 'N/A')}")
            with col3:
                st.write(f"**배점:** {question.get('points', 'N/A')}")
            
            if question.get('scenario'):
                st.write(f"**시나리오:** {question['scenario']}")
            
            # 시각적 요소 표시
            if question.get('visual_image'):
                st.markdown("**📊 시각 자료:**")
                image_html = f'<img src="data:image/png;base64,{question["visual_image"]}" style="max-width:100%; height:auto; border: 1px solid #ddd; border-radius: 8px; margin: 10px 0;">'
                st.markdown(image_html, unsafe_allow_html=True)
                st.markdown("---")
            
            st.write(f"**문제:** {question.get('question', 'N/A')}")
            
            # 답안 표시 (기존과 동일)
            UIComponents._display_answer_section(question)
            
            st.caption(f"과목: {question.get('subject_area', 'N/A')}")
    
    @staticmethod
    def _display_answer_section(question: Dict[str, Any]):
        """답안 섹션 표시"""
        if question.get('question_type') == '선다형' and question.get('choices'):
            for choice in question['choices']:
                st.write(choice)
            st.success(f"**정답:** {question.get('correct_answer', 'N/A')}")
        elif question.get('question_type') == '단답형':
            st.success(f"**정답:** {question.get('correct_answer', 'N/A')}")
            if question.get('alternative_answers'):
                alt_answers = question['alternative_answers']
                if isinstance(alt_answers, list):
                    alt_strings = []
                    for item in alt_answers:
                        if isinstance(item, str):
                            alt_strings.append(item)
                        elif isinstance(item, dict):
                            alt_strings.append(str(item.get('answer', item)))
                        else:
                            alt_strings.append(str(item))
                    
                    if alt_strings:
                        st.info(f"**가능한 답:** {', '.join(alt_strings)}")
        elif question.get('question_type') == '서술형':
            st.success(f"**모범답안:** {question.get('model_answer', 'N/A')}")
            if question.get('grading_criteria'):
                st.info("**채점기준:**")
                for i, criteria in enumerate(question['grading_criteria'], 1):
                    st.write(f"{i}. {criteria}")
        
        if question.get('explanation'):
            st.write(f"**해설:** {question['explanation']}")
    
    @staticmethod
    def display_statistics_charts(questions: List[Dict[str, Any]]):
        """통계 차트 표시"""
        stats = generate_statistics(questions)
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 문제수", stats["총_문제수"])
        with col2:
            st.metric("시각적 문제", stats["시각적_요소_통계"]["시각적_문제수"])
        with col3:
            st.metric("텍스트 문제", stats["시각적_요소_통계"]["텍스트_문제수"])
        with col4:
            st.metric("시각적 비율", f"{stats['시각적_요소_통계']['시각적_비율']}%")
        
        # 차트 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 문제 유형별 분포 차트
            type_data = stats["문제_유형별_분포"]
            fig_type = px.pie(
                values=list(type_data.values()),
                names=list(type_data.keys()),
                title="문제 유형별 분포"
            )
            st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            # 난이도별 분포 차트
            diff_data = stats["난이도별_분포"]
            fig_diff = px.bar(
                x=list(diff_data.keys()),
                y=list(diff_data.values()),
                title="난이도별 분포",
                color=list(diff_data.keys())
            )
            st.plotly_chart(fig_diff, use_container_width=True)
        
        with col3:
            # 시각적 요소 vs 텍스트 비교
            visual_stats = stats["시각적_요소_통계"]
            fig_visual = px.pie(
                values=[visual_stats["시각적_문제수"], visual_stats["텍스트_문제수"]],
                names=["시각적 문제", "텍스트 문제"],
                title="시각적 요소 분포"
            )
            st.plotly_chart(fig_visual, use_container_width=True)
        
        # 시각적 요소 유형별 분포 (있는 경우만)
        if stats["시각적_요소_통계"]["시각요소_유형별"]:
            st.subheader("🎨 시각적 요소 유형별 분포")
            visual_types = stats["시각적_요소_통계"]["시각요소_유형별"]
            fig_visual_types = px.bar(
                x=list(visual_types.keys()),
                y=list(visual_types.values()),
                title="시각적 요소 유형별 분포"
            )
            st.plotly_chart(fig_visual_types, use_container_width=True)