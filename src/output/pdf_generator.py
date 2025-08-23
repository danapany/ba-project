# src/output/pdf_generator.py
"""
PDF 문서 생성 모듈
시각적 요소를 포함한 PDF 문제집 생성
"""

import os
import random
import base64
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import Image as ReportLabImage
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from PIL import Image as PILImage

from utils.utils import setup_korean_font, safe_text_escape, generate_statistics, cleanup_temp_files
import streamlit as st

class PDFGenerator:
    """PDF 문제집 생성기"""
    
    def __init__(self):
        self.korean_font_available = setup_korean_font()
        self.font_name = 'KoreanFont' if self.korean_font_available else 'Helvetica'
        self.temp_dir = "temp/images"
        
        if not self.korean_font_available:
            st.warning("⚠️ 한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
    
    def _setup_styles(self):
        """PDF 스타일 설정"""
        styles = getSampleStyleSheet()
        
        return {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER,
                wordWrap='CJK'
            ),
            'question_title': ParagraphStyle(
                'QuestionTitle',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=12,
                spaceAfter=12,
                spaceBefore=20,
                wordWrap='CJK'
            ),
            'question': ParagraphStyle(
                'Question',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                spaceAfter=8,
                leftIndent=20,
                wordWrap='CJK'
            ),
            'answer': ParagraphStyle(
                'Answer',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=9,
                spaceAfter=8,
                leftIndent=40,
                wordWrap='CJK'
            ),
            'normal': ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10,
                wordWrap='CJK'
            )
        }
    
    def _create_temp_dir(self):
        """임시 디렉토리 생성"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def _process_visual_image(self, question: Dict[str, Any], question_num: int) -> ReportLabImage:
        """시각적 이미지 처리 및 ReportLab Image 객체 생성"""
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
            temp_image_path = os.path.join(self.temp_dir, f"temp_image_{question_num}_{random.randint(1000, 9999)}.png")
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
            
            # ReportLab Image 객체 생성
            img = ReportLabImage(temp_image_path, width=final_width, height=final_height)
            print(f"이미지 추가 성공: 문제 {question_num}")
            return img
            
        except Exception as e:
            print(f"이미지 처리 실패 (문제 {question_num}): {e}")
            return None
    
    def _add_title_page(self, story: list, styles: dict, total_questions: int):
        """제목 페이지 추가"""
        story.append(Paragraph("Business Application 모델링", styles['title']))
        story.append(Paragraph("문제집", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}", styles['normal']))
        story.append(Paragraph(f"총 문제수: {total_questions}개", styles['normal']))
        story.append(PageBreak())
    
    def _add_statistics_page(self, story: list, styles: dict, questions: List[Dict[str, Any]]):
        """통계 페이지 추가"""
        stats = generate_statistics(questions)
        story.append(Paragraph("문제 통계", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        
        # 문제 유형별 분포
        story.append(Paragraph("1. 문제 유형별 분포", styles['question_title']))
        for q_type, count in stats["문제_유형별_분포"].items():
            story.append(Paragraph(f"• {q_type}: {count}개", styles['question']))
        
        story.append(Spacer(1, 0.1*inch))
        
        # 난이도별 분포
        story.append(Paragraph("2. 난이도별 분포", styles['question_title']))
        for difficulty, count in stats["난이도별_분포"].items():
            story.append(Paragraph(f"• {difficulty}: {count}개", styles['question']))
        
        # 시각적 문제 통계 추가
        visual_count = sum(1 for q in questions if q.get('visual_image'))
        if visual_count > 0:
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph("3. 시각적 요소 포함 문제", styles['question_title']))
            story.append(Paragraph(f"• 시각적 문제: {visual_count}개", styles['question']))
            story.append(Paragraph(f"• 텍스트 문제: {len(questions) - visual_count}개", styles['question']))
        
        story.append(PageBreak())
    
    def _add_question_section(self, story: list, styles: dict, questions: List[Dict[str, Any]]):
        """문제 섹션 추가"""
        story.append(Paragraph("문제", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, question in enumerate(questions, 1):
            try:
                # 문제 번호와 제목
                title = question.get('title', f'문제 {i}')
                safe_title = safe_text_escape(title)
                story.append(Paragraph(f"문제 {i}. {safe_title}", styles['question_title']))
                
                # 문제 정보
                info_text = f"유형: {safe_text_escape(question.get('question_type'))} | "
                info_text += f"난이도: {safe_text_escape(question.get('difficulty'))} | "
                info_text += f"배점: {safe_text_escape(question.get('points'))}점"
                if question.get('visual_type'):
                    info_text += f" | 시각요소: {question['visual_type'].upper()}"
                story.append(Paragraph(info_text, styles['answer']))
                
                # 시나리오
                if question.get('scenario'):
                    scenario_text = safe_text_escape(question['scenario'])
                    story.append(Paragraph(f"[시나리오] {scenario_text}", styles['question']))
                    story.append(Spacer(1, 0.05*inch))
                
                # 시각적 요소가 있는 경우 이미지 처리
                if question.get('visual_image'):
                    img = self._process_visual_image(question, i)
                    if img:
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                    else:
                        story.append(Paragraph(f"[시각 자료: {question.get('visual_type', 'Image').upper()} - 표시 오류]", styles['question']))
                        story.append(Spacer(1, 0.1*inch))
                
                # 문제 내용
                question_text = safe_text_escape(question.get('question'))
                story.append(Paragraph(f"문제: {question_text}", styles['question']))
                story.append(Spacer(1, 0.1*inch))
                
                # 선다형 선택지
                if question.get('question_type') == '선다형' and question.get('choices'):
                    for choice in question['choices']:
                        safe_choice = safe_text_escape(choice)
                        story.append(Paragraph(safe_choice, styles['answer']))
                
                story.append(Spacer(1, 0.2*inch))
                
                # 페이지 구분 (시각적 요소가 있는 경우 더 적게, 없는 경우 더 많이)
                questions_per_page = 1 if question.get('visual_image') else 3
                if i % questions_per_page == 0 and i < len(questions):
                    story.append(PageBreak())
                    
            except Exception as question_error:
                print(f"문제 {i} 처리 중 오류: {question_error}")
                story.append(Paragraph(f"문제 {i}: 처리 오류 발생", styles['question']))
    
    def _add_integrated_questions(self, story: list, styles: dict, questions: List[Dict[str, Any]]):
        """통합형: 문제와 정답/해설을 함께 표시"""
        story.append(Paragraph("문제 및 정답", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, question in enumerate(questions, 1):
            try:
                # 문제 번호와 제목
                title = question.get('title', f'문제 {i}')
                safe_title = safe_text_escape(title)
                story.append(Paragraph(f"문제 {i}. {safe_title}", styles['question_title']))
                
                # 문제 정보
                info_text = f"유형: {safe_text_escape(question.get('question_type'))} | "
                info_text += f"난이도: {safe_text_escape(question.get('difficulty'))} | "
                info_text += f"배점: {safe_text_escape(question.get('points'))}점"
                if question.get('visual_type'):
                    info_text += f" | 시각요소: {question['visual_type'].upper()}"
                story.append(Paragraph(info_text, styles['answer']))
                
                # 시나리오
                if question.get('scenario'):
                    scenario_text = safe_text_escape(question['scenario'])
                    story.append(Paragraph(f"[시나리오] {scenario_text}", styles['question']))
                    story.append(Spacer(1, 0.05*inch))
                
                # 시각적 요소가 있는 경우 이미지 처리
                if question.get('visual_image'):
                    img = self._process_visual_image(question, i)
                    if img:
                        story.append(img)
                        story.append(Spacer(1, 0.2*inch))
                    else:
                        story.append(Paragraph(f"[시각 자료: {question.get('visual_type', 'Image').upper()} - 표시 오류]", styles['question']))
                        story.append(Spacer(1, 0.1*inch))
                
                # 문제 내용
                question_text = safe_text_escape(question.get('question'))
                story.append(Paragraph(f"문제: {question_text}", styles['question']))
                story.append(Spacer(1, 0.1*inch))
                
                # 선다형 선택지
                if question.get('question_type') == '선다형' and question.get('choices'):
                    for choice in question['choices']:
                        safe_choice = safe_text_escape(choice)
                        story.append(Paragraph(safe_choice, styles['answer']))
                
                story.append(Spacer(1, 0.15*inch))
                
                # 정답 및 해설 (통합형에서는 바로 표시)
                self._add_single_answer(story, styles, question, i)
                
                story.append(Spacer(1, 0.3*inch))
                
                # 페이지 구분 (시각적 요소가 있으면 1문제당 1페이지, 없으면 2문제당 1페이지)
                questions_per_page = 1 if question.get('visual_image') else 2
                if i % questions_per_page == 0 and i < len(questions):
                    story.append(PageBreak())
                    
            except Exception as question_error:
                print(f"문제 {i} 처리 중 오류: {question_error}")
                story.append(Paragraph(f"문제 {i}: 처리 오류 발생", styles['question']))
    
    def _add_single_answer(self, story: list, styles: dict, question: Dict[str, Any], question_num: int):
        """개별 문제의 정답 및 해설 추가"""
        try:
            # 정답 표시
            story.append(Paragraph("정답 및 해설", styles['question_title']))
            
            # 정답
            if question.get('question_type') == '선다형':
                story.append(Paragraph(f"정답: {safe_text_escape(question.get('correct_answer'))}", styles['question']))
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
                story.append(Paragraph(answer_text, styles['question']))
            elif question.get('question_type') == '서술형':
                model_answer = safe_text_escape(question.get('model_answer'))
                story.append(Paragraph(f"모범답안: {model_answer}", styles['question']))
                
                # 채점기준 처리
                if question.get('grading_criteria'):
                    try:
                        story.append(Paragraph("채점기준:", styles['question']))
                        criteria_list = question['grading_criteria']
                        
                        if isinstance(criteria_list, list):
                            for j, criteria in enumerate(criteria_list, 1):
                                safe_criteria = safe_text_escape(criteria)
                                story.append(Paragraph(f"{j}. {safe_criteria}", styles['answer']))
                        else:
                            safe_criteria = safe_text_escape(criteria_list)
                            story.append(Paragraph(f"1. {safe_criteria}", styles['answer']))
                    except Exception:
                        story.append(Paragraph("채점기준: 처리 오류", styles['answer']))
            
            # 해설
            if question.get('explanation'):
                explanation_text = safe_text_escape(question['explanation'])
                story.append(Paragraph(f"해설: {explanation_text}", styles['question']))
            
        except Exception as answer_error:
            print(f"문제 {question_num} 정답 처리 중 오류: {answer_error}")
            story.append(Paragraph(f"정답 {question_num}: 처리 오류 발생", styles['question']))
    
    def _add_answer_section(self, story: list, styles: dict, questions: List[Dict[str, Any]]):
        """정답 및 해설 섹션 추가"""
        story.append(PageBreak())
        story.append(Paragraph("정답 및 해설", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        
        for i, question in enumerate(questions, 1):
            try:
                story.append(Paragraph(f"문제 {i}.", styles['question_title']))
                
                # 정답
                if question.get('question_type') == '선다형':
                    story.append(Paragraph(f"정답: {safe_text_escape(question.get('correct_answer'))}", styles['question']))
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
                    story.append(Paragraph(answer_text, styles['question']))
                elif question.get('question_type') == '서술형':
                    model_answer = safe_text_escape(question.get('model_answer'))
                    story.append(Paragraph(f"모범답안: {model_answer}", styles['question']))
                    
                    # 채점기준 처리
                    if question.get('grading_criteria'):
                        try:
                            story.append(Paragraph("채점기준:", styles['question']))
                            criteria_list = question['grading_criteria']
                            
                            if isinstance(criteria_list, list):
                                for j, criteria in enumerate(criteria_list, 1):
                                    safe_criteria = safe_text_escape(criteria)
                                    story.append(Paragraph(f"{j}. {safe_criteria}", styles['answer']))
                            else:
                                safe_criteria = safe_text_escape(criteria_list)
                                story.append(Paragraph(f"1. {safe_criteria}", styles['answer']))
                        except Exception:
                            story.append(Paragraph("채점기준: 처리 오류", styles['answer']))
                
                # 해설
                if question.get('explanation'):
                    explanation_text = safe_text_escape(question['explanation'])
                    story.append(Paragraph(f"해설: {explanation_text}", styles['question']))
                
                story.append(Spacer(1, 0.15*inch))
                
                # 페이지 구분 (8문제마다)
                if i % 8 == 0 and i < len(questions):
                    story.append(PageBreak())
                    
            except Exception as question_error:
                print(f"문제 {i} 처리 중 오류: {question_error}")
                story.append(Paragraph(f"문제 {i}: 처리 오류 발생", styles['question']))
    
    def create_pdf_document_with_images(self, questions: List[Dict[str, Any]], format_type: str = "separated") -> bytes:
        """시각적 요소를 포함한 PDF 생성"""
        buffer = BytesIO()
        self._create_temp_dir()
        
        try:
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # 스타일 설정
            styles = self._setup_styles()
            story = []
            
            # 페이지 섹션들 추가
            self._add_title_page(story, styles, len(questions))
            self._add_statistics_page(story, styles, questions)
            
            if format_type == "integrated":
                # 통합형: 문제와 정답/해설을 함께 표시
                self._add_integrated_questions(story, styles, questions)
            else:
                # 분리형: 문제 먼저, 정답/해설 나중에
                self._add_question_section(story, styles, questions)
                self._add_answer_section(story, styles, questions)
            
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
            cleanup_temp_files(self.temp_dir)