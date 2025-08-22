# main_app.py
"""
메인 Streamlit 애플리케이션
UI, PDF 생성, 파일 다운로드, 통계 등을 담당
"""

import streamlit as st
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import zipfile
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
# 여기가 중요한 부분 - ReportLab Image를 명시적으로 import
from reportlab.platypus.flowables import Image as ReportLabImage
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request
import platform
import base64
# PIL Image는 다른 이름으로 import
from PIL import Image as PILImage

# 로컬 모듈 import
from question_generator import BAQuestionGenerator
from visual_generator import EnhancedBAQuestionGenerator

# A4 페이지 크기 상수 (debugging용)
print(f"A4 페이지 크기: {A4[0]} x {A4[1]} points")
print(f"A4 가로폭(인치): {A4[0]/72:.2f} inch")
print(f"A4 세로폭(인치): {A4[1]/72:.2f} inch")

# .env 파일 로드
load_dotenv()

# 환경변수 설정
AZURE_OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')
AZURE_OPENAI_KEY = os.getenv('OPENAI_KEY')
AZURE_DEPLOYMENT_NAME = os.getenv('CHAT_MODEL3')
AZURE_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
DEFAULT_QUESTION_COUNT = int(os.getenv('DEFAULT_QUESTION_COUNT', 50))
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# 페이지 설정
st.set_page_config(
    page_title="BA 문제 생성기",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def setup_korean_font():
    """한글 폰트 설정"""
    try:
        # 시스템별 기본 한글 폰트 경로
        system = platform.system()
        font_paths = []
        
        if system == "Windows":
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # 맑은 고딕
                "C:/Windows/Fonts/gulim.ttc",   # 굴림
                "C:/Windows/Fonts/batang.ttc",  # 바탕
            ]
        elif system == "Darwin":  # macOS
            font_paths = [
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/Library/Fonts/Arial Unicode MS.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        else:  # Linux
            font_paths = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/NanumGothic.ttf",
            ]
        
        # 폰트 파일 찾기 및 등록
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                    font_registered = True
                    print(f"한글 폰트 등록 성공: {font_path}")
                    break
                except Exception as e:
                    print(f"폰트 등록 실패 {font_path}: {e}")
                    continue
        
        if not font_registered:
            # 온라인에서 나눔고딕 다운로드 시도
            try:
                nanum_url = "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothic.ttf"
                font_data = urllib.request.urlopen(nanum_url).read()
                
                # 임시 파일로 저장
                temp_font_path = "temp_nanum.ttf"
                with open(temp_font_path, 'wb') as f:
                    f.write(font_data)
                
                pdfmetrics.registerFont(TTFont('KoreanFont', temp_font_path))
                font_registered = True
                print("나눔고딕 온라인 다운로드 및 등록 성공")
                
                # 임시 파일 삭제
                if os.path.exists(temp_font_path):
                    os.remove(temp_font_path)
                    
            except Exception as e:
                print(f"온라인 폰트 다운로드 실패: {e}")
        
        return font_registered
        
    except Exception as e:
        print(f"폰트 설정 중 오류 발생: {e}")
        return False

def check_azure_config():
    """Azure OpenAI 설정 확인"""
    env_exists = os.path.exists('.env')
    
    required_vars = {
        'OPENAI_ENDPOINT': AZURE_OPENAI_ENDPOINT,
        'OPENAI_KEY': AZURE_OPENAI_KEY,
        'CHAT_MODEL3': AZURE_DEPLOYMENT_NAME,
        'AZURE_OPENAI_API_VERSION': AZURE_API_VERSION
    }
    
    configured_vars = {k: bool(v) for k, v in required_vars.items()}
    all_configured = all(configured_vars.values())
    
    return {
        'env_file_exists': env_exists,
        'azure_configured': all_configured,
        'configured_vars': configured_vars,
        'endpoint': AZURE_OPENAI_ENDPOINT[:30] + '...' if AZURE_OPENAI_ENDPOINT else None,
        'deployment_name': AZURE_DEPLOYMENT_NAME
    }

def create_env_file_template():
    """환경 설정 파일 템플릿 생성"""
    template = """# Azure OpenAI 설정
OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
OPENAI_KEY=your-azure-openai-api-key-here
CHAT_MODEL3=your-deployment-name

# API 버전 (선택사항)
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# 기타 설정 (선택사항)
DEFAULT_QUESTION_COUNT=100

# 디버그 모드 (개발용)
DEBUG=False
"""
    return template

def create_pdf_document_with_images(questions: List[Dict[str, Any]]) -> bytes:
    """시각적 요소를 포함한 PDF 생성 (수정된 버전)"""
    
    def safe_text_escape(text):
        """텍스트를 안전하게 HTML 이스케이프 처리"""
        if text is None:
            return 'N/A'
        
        # 다양한 데이터 타입을 문자열로 변환
        if isinstance(text, str):
            text_str = text
        elif isinstance(text, dict):
            # 딕셔너리인 경우 적절한 값 추출
            text_str = text.get('text', text.get('description', text.get('value', str(text))))
        elif isinstance(text, list):
            # 리스트인 경우 첫 번째 항목 사용 또는 전체를 문자열로
            text_str = str(text[0]) if text else ''
        else:
            text_str = str(text)
        
        # HTML 특수문자 이스케이프
        return text_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    buffer = BytesIO()
    
    # 한글 폰트 설정
    korean_font_available = setup_korean_font()
    font_name = 'KoreanFont' if korean_font_available else 'Helvetica'
    
    if not korean_font_available:
        st.warning("⚠️ 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    
    # PDF 문서 생성
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    # 스타일 설정 (기존과 동일)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        wordWrap='CJK'
    )
    
    question_title_style = ParagraphStyle(
        'QuestionTitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=12,
        spaceAfter=12,
        spaceBefore=20,
        wordWrap='CJK'
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        spaceAfter=8,
        leftIndent=20,
        wordWrap='CJK'
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        spaceAfter=8,
        leftIndent=40,
        wordWrap='CJK'
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        wordWrap='CJK'
    )
    
    # PDF 내용 구성
    story = []
    
    # 제목 페이지
    story.append(Paragraph("Business Application 모델링", title_style))
    story.append(Paragraph("문제집", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}", normal_style))
    story.append(Paragraph(f"총 문제수: {len(questions)}개", normal_style))
    story.append(PageBreak())
    
    # 통계 페이지 (기존과 동일)
    stats = generate_statistics(questions)
    story.append(Paragraph("문제 통계", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 문제 유형별 분포
    story.append(Paragraph("1. 문제 유형별 분포", question_title_style))
    for q_type, count in stats["문제_유형별_분포"].items():
        story.append(Paragraph(f"• {q_type}: {count}개", question_style))
    
    story.append(Spacer(1, 0.1*inch))
    
    # 난이도별 분포
    story.append(Paragraph("2. 난이도별 분포", question_title_style))
    for difficulty, count in stats["난이도별_분포"].items():
        story.append(Paragraph(f"• {difficulty}: {count}개", question_style))
    
    # 시각적 문제 통계 추가
    visual_count = sum(1 for q in questions if q.get('visual_image'))
    if visual_count > 0:
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("3. 시각적 요소 포함 문제", question_title_style))
        story.append(Paragraph(f"• 시각적 문제: {visual_count}개", question_style))
        story.append(Paragraph(f"• 텍스트 문제: {len(questions) - visual_count}개", question_style))
    
    story.append(PageBreak())
    
    # 문제 내용
    story.append(Paragraph("문제", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 임시 이미지 파일 저장용 디렉토리 생성
    temp_dir = "temp_images"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        for i, question in enumerate(questions, 1):
            # 문제 번호와 제목
            title = question.get('title', f'문제 {i}')
            safe_title = safe_text_escape(title)
            story.append(Paragraph(f"문제 {i}. {safe_title}", question_title_style))
            
            # 문제 정보
            info_text = f"유형: {safe_text_escape(question.get('question_type'))} | "
            info_text += f"난이도: {safe_text_escape(question.get('difficulty'))} | "
            info_text += f"배점: {safe_text_escape(question.get('points'))}점"
            if question.get('visual_type'):
                info_text += f" | 시각요소: {question['visual_type'].upper()}"
            story.append(Paragraph(info_text, answer_style))
            
            # 시나리오
            if question.get('scenario'):
                scenario_text = safe_text_escape(question['scenario'])
                story.append(Paragraph(f"[시나리오] {scenario_text}", question_style))
                story.append(Spacer(1, 0.05*inch))
            
            # 시각적 요소가 있는 경우 이미지 처리 (수정된 부분)
            if question.get('visual_image'):
                try:
                    # base64 이미지를 PIL Image로 변환
                    image_data = base64.b64decode(question['visual_image'])
                    pil_image = PILImage.open(BytesIO(image_data))
                    
                    # 이미지를 RGB 모드로 변환 (투명도 제거)
                    if pil_image.mode in ('RGBA', 'LA'):
                        background = PILImage.new('RGB', pil_image.size, (255, 255, 255))
                        if pil_image.mode == 'RGBA':
                            background.paste(pil_image, mask=pil_image.split()[-1])
                        else:
                            background.paste(pil_image, mask=pil_image.split()[-1])
                        pil_image = background
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # 임시 파일로 저장 (고유한 파일명 사용)
                    temp_image_path = os.path.join(temp_dir, f"temp_image_{i}_{random.randint(1000, 9999)}.png")
                    pil_image.save(temp_image_path, 'PNG', quality=95)
                    
                    # 이미지 크기 조정 (A4 페이지 가로폭의 90%로 제한)
                    img_width, img_height = pil_image.size
                    
                    # A4 페이지의 실제 사용 가능한 가로폭 (여백 제외)
                    page_width = A4[0] - 2 * inch  # A4 너비에서 좌우 여백 제외
                    max_width = page_width * 0.9   # 페이지 가로폭의 90%
                    max_height = 5 * inch          # 세로는 5인치로 제한
                    
                    # 비율 유지하면서 크기 조정
                    width_ratio = max_width / img_width
                    height_ratio = max_height / img_height
                    scale_ratio = min(width_ratio, height_ratio)  # 페이지에 맞게 조정
                    
                    final_width = img_width * scale_ratio
                    final_height = img_height * scale_ratio
                    
                    # ReportLab Image 객체 생성 (수정된 부분)
                    try:
                        # ReportLabImage 사용 (이름 충돌 해결)
                        img = ReportLabImage(temp_image_path, width=final_width, height=final_height)
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                        print(f"이미지 추가 성공: 문제 {i}")
                    except Exception as img_error:
                        print(f"ReportLab 이미지 생성 실패: {img_error}")
                        story.append(Paragraph(f"[시각 자료: {question.get('visual_type', 'Image').upper()} - 표시 오류]", question_style))
                        story.append(Spacer(1, 0.1*inch))
                        
                except Exception as e:
                    print(f"이미지 처리 실패 (문제 {i}): {e}")
                    # 이미지 처리 실패 시 텍스트로 대체
                    story.append(Paragraph(f"[시각 자료: {question.get('visual_type', 'Image').upper()}]", question_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # 문제 내용
            question_text = safe_text_escape(question.get('question'))
            story.append(Paragraph(f"문제: {question_text}", question_style))
            story.append(Spacer(1, 0.1*inch))
            
            # 선다형 선택지
            if question.get('question_type') == '선다형' and question.get('choices'):
                for choice in question['choices']:
                    safe_choice = safe_text_escape(choice)
                    story.append(Paragraph(safe_choice, answer_style))
            
            story.append(Spacer(1, 0.2*inch))
            
            # 페이지 구분 (시각적 요소가 있는 경우 더 적게, 없는 경우 더 많이)
            questions_per_page = 1 if question.get('visual_image') else 3  # 시각적 문제는 1개씩, 텍스트 문제는 3개씩
            if i % questions_per_page == 0 and i < len(questions):
                story.append(PageBreak())
        
        # 정답 및 해설 페이지 (기존과 동일하지만 이미지는 제외)
        story.append(PageBreak())
        story.append(Paragraph("정답 및 해설", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        for i, question in enumerate(questions, 1):
            try:
                story.append(Paragraph(f"문제 {i}.", question_title_style))
                
                # 정답
                if question.get('question_type') == '선다형':
                    story.append(Paragraph(f"정답: {safe_text_escape(question.get('correct_answer'))}", question_style))
                elif question.get('question_type') == '단답형':
                    answer_text = f"정답: {safe_text_escape(question.get('correct_answer'))}"
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
                                answer_text += f" (가능한 답: {', '.join(alt_strings)})"
                    story.append(Paragraph(answer_text, question_style))
                elif question.get('question_type') == '서술형':
                    model_answer = safe_text_escape(question.get('model_answer'))
                    story.append(Paragraph(f"모범답안: {model_answer}", question_style))
                    
                    # 채점기준 처리 (더 안전하게)
                    if question.get('grading_criteria'):
                        try:
                            story.append(Paragraph("채점기준:", question_style))
                            criteria_list = question['grading_criteria']
                            
                            if isinstance(criteria_list, list):
                                for j, criteria in enumerate(criteria_list, 1):
                                    safe_criteria = safe_text_escape(criteria)
                                    story.append(Paragraph(f"{j}. {safe_criteria}", answer_style))
                            else:
                                # 리스트가 아닌 경우
                                safe_criteria = safe_text_escape(criteria_list)
                                story.append(Paragraph(f"1. {safe_criteria}", answer_style))
                                
                        except Exception as criteria_error:
                            print(f"채점기준 처리 오류 (문제 {i}): {criteria_error}")
                            print(f"grading_criteria 타입: {type(question.get('grading_criteria'))}")
                            print(f"grading_criteria 값: {question.get('grading_criteria')}")
                            story.append(Paragraph("채점기준: 처리 오류", answer_style))
                
                # 해설
                if question.get('explanation'):
                    explanation_text = safe_text_escape(question['explanation'])
                    story.append(Paragraph(f"해설: {explanation_text}", question_style))
                
                story.append(Spacer(1, 0.15*inch))
                
                # 페이지 구분 (8문제마다)
                if i % 8 == 0 and i < len(questions):
                    story.append(PageBreak())
                    
            except Exception as question_error:
                print(f"문제 {i} 처리 중 오류: {question_error}")
                print(f"문제 {i} 데이터: {question}")
                story.append(Paragraph(f"문제 {i}: 처리 오류 발생", question_style))
        
        # PDF 생성
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"PDF 생성 중 오류 발생: {e}")
        print(f"PDF 생성 상세 오류: {e}")
        return b""
    
    finally:
        # 임시 이미지 파일들 정리
        try:
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(temp_dir)
        except Exception as cleanup_error:
            print(f"임시 파일 정리 중 오류: {cleanup_error}")

def create_download_files(questions: List[Dict[str, Any]]) -> bytes:
    """다운로드용 파일들을 ZIP으로 압축"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 파일 추가
        json_content = json.dumps(questions, ensure_ascii=False, indent=2)
        zip_file.writestr(f"BA_questions_{timestamp}.json", json_content.encode('utf-8'))
        
        # PDF 파일 추가
        pdf_data = create_pdf_document_with_images(questions)
        zip_file.writestr(f"BA_questions_{timestamp}.pdf", pdf_data)
        
        # Excel 파일 추가
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            for q_type in ["선다형", "단답형", "서술형"]:
                type_questions = [q for q in questions if q.get('question_type') == q_type]
                if type_questions:
                    df = pd.json_normalize(type_questions)
                    df.to_excel(writer, sheet_name=q_type, index=False)
        
        zip_file.writestr(f"BA_questions_{timestamp}.xlsx", excel_buffer.getvalue())
        
        # 통계 파일 추가
        stats = generate_statistics(questions)
        stats_content = json.dumps(stats, ensure_ascii=False, indent=2)
        zip_file.writestr(f"BA_question_stats_{timestamp}.json", stats_content.encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def generate_statistics(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """문제 생성 통계"""
    stats = {
        "총_문제수": len(questions),
        "생성_일시": datetime.now().isoformat(),
        "문제_유형별_분포": {},
        "난이도별_분포": {},
        "과목별_분포": {},
        "시각적_요소_통계": {}
    }
    
    visual_count = 0
    visual_types = {}
    
    for question in questions:
        q_type = question.get('question_type', '미분류')
        stats["문제_유형별_분포"][q_type] = stats["문제_유형별_분포"].get(q_type, 0) + 1
        
        difficulty = question.get('difficulty', '미분류')
        stats["난이도별_분포"][difficulty] = stats["난이도별_분포"].get(difficulty, 0) + 1
        
        subject = question.get('subject_area', '미분류')
        subject_short = subject.split(' > ')[-1] if ' > ' in subject else subject
        stats["과목별_분포"][subject_short] = stats["과목별_분포"].get(subject_short, 0) + 1
        
        # 시각적 요소 통계
        if question.get('visual_image'):
            visual_count += 1
            visual_type = question.get('visual_type', '기타')
            visual_types[visual_type] = visual_types.get(visual_type, 0) + 1
    
    stats["시각적_요소_통계"] = {
        "시각적_문제수": visual_count,
        "텍스트_문제수": len(questions) - visual_count,
        "시각적_비율": round(visual_count / len(questions) * 100, 1) if questions else 0,
        "시각요소_유형별": visual_types
    }
    
    return stats

def display_visual_question_in_main(question: Dict[str, Any], index: int):
    """메인 앱에서 시각적 문제 표시"""
    with st.expander(f"🔍 문제 {index + 1}: {question.get('title', '제목 없음')}", expanded=False):
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

def display_question(question: Dict[str, Any], index: int):
    """일반 문제 표시 (기존 함수)"""
    with st.expander(f"🔍 문제 {index + 1}: {question.get('title', '제목 없음')}", expanded=False):
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
            display_visual_question_in_main(st.session_state['demo_question'], 0)
        else:
            st.info("왼쪽에서 문제를 생성해보세요!")

def main():
    """메인 Streamlit 앱"""
    
    # Azure OpenAI 설정 확인
    azure_status = check_azure_config()
    
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
        if not azure_status['env_file_exists']:
            st.warning("⚠️ .env 파일이 없습니다. Azure OpenAI 설정을 확인해주세요.")
            
            with st.expander("🔧 Azure OpenAI 설정 도움말", expanded=True):
                st.markdown("### Azure OpenAI 설정 방법")
                st.markdown("1. Azure Portal에서 OpenAI 리소스를 생성하세요.")
                st.markdown("2. 모델을 배포하세요 (예: GPT-4, GPT-3.5-turbo).")
                st.markdown("3. 프로젝트 루트에 `.env` 파일을 생성하세요.")
                st.markdown("4. 아래 템플릿을 복사하여 붙여넣고 실제 값으로 변경하세요.")
                
                env_template = create_env_file_template()
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
        else:
            if azure_status['azure_configured']:
                st.success(f"✅ Azure OpenAI 설정 완료")
                st.info(f"🌐 엔드포인트: {azure_status['endpoint']}")
                st.info(f"🚀 배포 모델: {azure_status['deployment_name']}")
            else:
                st.error("❌ Azure OpenAI 설정이 완전하지 않습니다.")
                
                missing_vars = [k for k, v in azure_status['configured_vars'].items() if not v]
                st.error(f"누락된 환경변수: {', '.join(missing_vars)}")
        
        st.write("**Source PDF를 업로드하고 Azure OpenAI를 활용해 텍스트 + 시각적 요소가 포함된 고품질 문제를 생성해보세요!**")
        
        # 사이드바 설정
        with st.sidebar:
            # 문제 생성 설정
            st.subheader("📝 문제 설정")
            
            total_questions = st.slider(
                "총 문제 수",
                min_value=10,
                max_value=200,
                value=DEFAULT_QUESTION_COUNT,
                step=10
            )
            
            # 문제 유형별 비율 설정
            st.subheader("📊 문제 유형 비율")
            multiple_choice_ratio = st.slider("선다형 (%)", 0, 100, 60)
            short_answer_ratio = st.slider("단답형 (%)", 0, 100, 25)
            essay_ratio = 100 - multiple_choice_ratio - short_answer_ratio
            st.write(f"서술형: {essay_ratio}%")
            
            # 난이도 비율 설정
            st.subheader("🎯 난이도 비율")
            easy_ratio = st.slider("하 (%)", 0, 100, 50)
            medium_ratio = st.slider("중 (%)", 0, 100, 35)
            hard_ratio = 100 - easy_ratio - medium_ratio
            st.write(f"상: {hard_ratio}%")
            
            # 시각적 문제 비율 설정
            st.subheader("🎨 시각적 요소 설정")
            visual_ratio = st.slider("시각적 문제 비율 (%)", 0, 100, 30)
            st.caption("데이터 모델링, 프로세스 설계 등에서 ERD, UML, 플로우차트 등을 포함한 문제 생성")
            
            # 디버그 정보 (DEBUG=True일 때만 표시)
            if DEBUG_MODE:
                st.markdown("---")
                st.subheader("🛠 디버그 정보")
                st.json({
                    "env_file_exists": azure_status['env_file_exists'],
                    "azure_configured": azure_status['azure_configured'],
                    "configured_vars": azure_status['configured_vars'],
                    "deployment_name": azure_status['deployment_name'],
                    "endpoint": AZURE_OPENAI_ENDPOINT,
                    "debug_mode": True
                })
        
        # 메인 영역
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
                generator.visual_question_ratio = visual_ratio / 100
                
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
                generator.visual_question_ratio = visual_ratio / 100
                
                # Azure OpenAI 연결 확인
                if not generator.api_configured:
                    st.error("❌ Azure OpenAI 연결에 실패했습니다. 설정을 확인해주세요.")
                    return
                
                # 진행률 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 문제 유형별 분배 계산
                question_distribution = []
                
                # 유형별 개수 계산
                mc_count = int(total_questions * multiple_choice_ratio / 100)
                sa_count = int(total_questions * short_answer_ratio / 100)
                essay_count = total_questions - mc_count - sa_count
                
                for q_type, count in [("선다형", mc_count), ("단답형", sa_count), ("서술형", essay_count)]:
                    if count > 0:
                        # 난이도별 분배
                        easy_count = int(count * easy_ratio / 100)
                        medium_count = int(count * medium_ratio / 100)
                        hard_count = count - easy_count - medium_count
                        
                        for difficulty, diff_count in zip(["하", "중", "상"], [easy_count, medium_count, hard_count]):
                            for _ in range(diff_count):
                                subject = random.choice(generator.subject_areas)
                                question_distribution.append((q_type, subject, difficulty))
                
                # 문제 생성
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
                
                # 세션 상태에 결과 저장
                st.session_state['questions'] = questions
                st.session_state['generation_complete'] = True
                
                st.success(f"🎉 총 {len(questions)}개 문제 생성 완료! (시각적 요소 포함: {visual_generated}개)")
        
        # 결과 표시
        if 'questions' in st.session_state and st.session_state.get('generation_complete'):
            questions = st.session_state['questions']
            
            st.markdown("---")
            st.header("📊 생성 결과")
            
            # 통계 표시
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
            
            # 다운로드 버튼
            st.markdown("---")
            st.header("💾 결과 다운로드")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # ZIP 파일 다운로드 (전체)
                zip_data = create_download_files(questions)
                st.download_button(
                    label="📦 전체 파일 다운로드 (ZIP)",
                    data=zip_data,
                    file_name=f"BA_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    help="PDF, JSON, Excel, 통계 파일 모두 포함"
                )
            
            with col2:
                # PDF 파일 다운로드 (시각적 요소 포함)
                pdf_data = create_pdf_document_with_images(questions)
                st.download_button(
                    label="📄 PDF 문제집 다운로드",
                    data=pdf_data,
                    file_name=f"BA_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    help="시각적 요소가 포함된 출력용 PDF 문제집"
                )
            
            with col3:
                # JSON 파일 다운로드
                json_data = json.dumps(questions, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📊 JSON 데이터 다운로드",
                    data=json_data.encode('utf-8'),
                    file_name=f"BA_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    help="데이터 처리용 JSON 파일"
                )
            
            # 문제 미리보기
            st.markdown("---")
            st.header("👀 생성된 문제 미리보기")
            
            # 문제 유형별 탭
            tabs = st.tabs(["전체", "선다형", "단답형", "서술형", "시각적 문제"])
            
            with tabs[0]:  # 전체
                for i, question in enumerate(questions[:10]):  # 처음 10개만 표시
                    if question.get('visual_image'):
                        display_visual_question_in_main(question, i)
                    else:
                        display_question(question, i)
                
                if len(questions) > 10:
                    st.info(f"처음 10개 문제만 표시됩니다. 전체 {len(questions)}개 문제는 다운로드하여 확인하세요.")
            
            for tab_idx, q_type in enumerate(["선다형", "단답형", "서술형"], 1):
                with tabs[tab_idx]:
                    type_questions = [q for q in questions if q.get('question_type') == q_type]
                    
                    if type_questions:
                        for i, question in enumerate(type_questions[:5]):  # 타입별로 5개씩 표시
                            if question.get('visual_image'):
                                display_visual_question_in_main(question, i)
                            else:
                                display_question(question, i)
                        
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
                        display_visual_question_in_main(question, i)
                    
                    if len(visual_questions) > 5:
                        st.info(f"처음 5개 시각적 문제만 표시됩니다. (총 {len(visual_questions)}개)")
                else:
                    st.write("생성된 시각적 문제가 없습니다.")
            
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